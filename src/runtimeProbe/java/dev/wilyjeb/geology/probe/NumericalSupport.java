package dev.wilyjeb.geology.probe;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.google.gson.Gson;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Exact bits on matching native support; no production caller or tolerance. */
@EventBusSubscriber(modid="geology_runtime_probe")
public final class NumericalSupport {
    private static int serial;
    private static boolean capture;
    private static Map<String,Object> captured;
    static void captureNative(int row,int col,float[] values) throws Exception {
        if(capture)captured=write(row,col,values);
    }
    private static Map<String,Object> write(int row,int col,float[] values) throws Exception {
        Path folder=Path.of("numerical-bits");Files.createDirectories(folder);
        String name=String.format("%03d-c%d-r%d-m0.bin",++serial,col,row);
        try(var out=new DataOutputStream(Files.newOutputStream(folder.resolve(name)))) {
            for(float v:values){if(!Float.isFinite(v))throw new IllegalStateException("Nonfinite");out.writeInt(Float.floatToRawIntBits(v));}
        }
        return Map.of("file",name,"col",col,"row",row,"mode",0,"samples",values.length,
            "requests",List.of(List.of(row*256,col*256,(row+1)*256,(col+1)*256)),"seed",LocalTerrainProvider.getSeed());
    }
    private static int size(Class<?> type,String name) throws Exception {
        var field=type.getDeclaredField(name);field.setAccessible(true);
        var map=(Map<?,?>)field.get(null);synchronized(map){return map.size();}
    }
    private static int send(net.minecraft.commands.CommandSourceStack source,Object value) {
        String json="ACCEPTANCE "+new Gson().toJson(value);
        org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info(json);
        source.sendSuccess(()->Component.literal(json),false);return 1;
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("acceptance").requires(s->s.hasPermission(4))
            .then(Commands.literal("numeric-control").then(Commands.argument("action",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->{
                try {
                    var source=c.getSource();dev.wilyjeb.geology.WorldGeologySettings.current(source.getServer());
                    String action=com.mojang.brigadier.arguments.StringArgumentType.getString(c,"action");
                    if(action.equals("prime-left")||action.equals("prime-right")) {
                        var method=SamplingDiagnostic.class.getDeclaredMethod("nativeCell",net.minecraft.server.MinecraftServer.class,int.class,int.class);
                        method.setAccessible(true);captured=null;capture=true;
                        try {method.invoke(null,source.getServer(),-14,action.equals("prime-left")?-6:6);}
                        finally {capture=false;}
                        if(captured==null)throw new IllegalStateException("Expected real diagnostic cache miss");
                        return send(source,captured);
                    }
                    int fineBefore=size(SamplingDiagnostic.class,"FINE"),providerBefore=size(LocalTerrainProvider.class,"CACHE");
                    if(action.equals("diagnostic-clear"))SamplingDiagnostic.clear();
                    else if(action.equals("provider-clear"))LocalTerrainProvider.clearCache();
                    else if(!action.equals("observe"))throw new IllegalArgumentException(action);
                    return send(source,Map.of("action",action,"fine_before",fineBefore,"fine_after",size(SamplingDiagnostic.class,"FINE"),
                        "provider_before",providerBefore,"provider_after",size(LocalTerrainProvider.class,"CACHE"),
                        "pending",size(LocalTerrainProvider.class,"PENDING"),"tensor_reset",false));
                }catch(Exception e){throw new IllegalStateException(e);}
            }))));
        event.getDispatcher().register(Commands.literal("acceptance").requires(s->s.hasPermission(4))
            .then(Commands.literal("numeric").then(Commands.argument("col",IntegerArgumentType.integer(-80,80))
            .then(Commands.argument("row",IntegerArgumentType.integer(-80,80))
            .then(Commands.argument("mode",IntegerArgumentType.integer(0,3)).executes(c->{
                try {
                    dev.wilyjeb.geology.WorldGeologySettings.current(c.getSource().getServer());
                    int col=IntegerArgumentType.getInteger(c,"col"),row=IntegerArgumentType.getInteger(c,"row"),mode=IntegerArgumentType.getInteger(c,"mode");
                    int x=col*256,z=row*256;float[] values=new float[65536];var requests=new ArrayList<List<Integer>>();
                    if(mode==2) {
                        for(int half=0;half<2;half++) {
                            int top=z+half*128;requests.add(List.of(top,x,top+128,x+256));
                            float[] a=LocalTerrainProvider.getPipelineData(top,x,top+128,x+256,false)[0];
                            if(a.length!=32768)throw new IllegalStateException("Batch shape");
                            System.arraycopy(a,0,values,half*32768,32768);
                        }
                    } else {
                        int halo=mode==1?1:0;
                        if(mode==3) {
                            requests.add(List.of(z,x,z+1,x+1));
                            values=LocalTerrainProvider.getPipelineData(z,x,z+1,x+1,false)[0];
                        } else {
                            requests.add(List.of(z-halo,x-halo,z+256+halo,x+256+halo));
                            float[] a=LocalTerrainProvider.getPipelineData(z-halo,x-halo,z+256+halo,x+256+halo,false)[0];
                            int n=256+2*halo;if(a.length!=n*n)throw new IllegalStateException("Halo shape");
                            for(int r=0;r<256;r++)System.arraycopy(a,(r+halo)*n+halo,values,r*256,256);
                        }
                    }
                    Path folder=Path.of("numerical-bits");Files.createDirectories(folder);
                    String name=String.format("%03d-c%d-r%d-m%d.bin",++serial,col,row,mode);
                    try(var out=new DataOutputStream(Files.newOutputStream(folder.resolve(name)))) {
                        for(float v:values){if(!Float.isFinite(v))throw new IllegalStateException("Nonfinite");out.writeInt(Float.floatToRawIntBits(v));}
                    }
                    var result=Map.of("file",name,"col",col,"row",row,"mode",mode,"samples",values.length,"requests",requests,"seed",LocalTerrainProvider.getSeed());
                    String json="ACCEPTANCE "+new Gson().toJson(result);
                    org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info(json);
                    c.getSource().sendSuccess(()->Component.literal(json),false);return 1;
                } catch(Exception e){throw new IllegalStateException(e);}
            }))))));
    }
}
