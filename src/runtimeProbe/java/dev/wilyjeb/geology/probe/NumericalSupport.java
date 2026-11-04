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
    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
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
