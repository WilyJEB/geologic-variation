package dev.wilyjeb.geology.probe;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.google.gson.Gson;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import dev.wilyjeb.geology.WorldGeologySettings;
import java.util.*;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/** Opt-in diagnostic only. One bounded patch, native coordinates, no production caller. */
@EventBusSubscriber(modid="geology_runtime_probe")
public final class TrackingPatch {
    private static MinecraftServer owner;
    private static long seed;
    private static int col, row;
    private static float[][] grid;
    private static String digest;
    private TrackingPatch() {}
    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("acceptance").requires(s -> s.hasPermission(4))
            .then(Commands.literal("track-clear").executes(c -> {
                grid=null;owner=null;
                String json="ACCEPTANCE {\"cleared\":true}";
                c.getSource().sendSuccess(() -> Component.literal(json),false);return 1;
            }))
            .then(Commands.literal("track-patch").then(Commands.argument("col",IntegerArgumentType.integer(-80,80))
                .then(Commands.argument("row",IntegerArgumentType.integer(-80,80))
                    .then(Commands.argument("band",IntegerArgumentType.integer(0,48)).executes(c -> {
                        var value=band(c.getSource().getServer(),IntegerArgumentType.getInteger(c,"col"),
                            IntegerArgumentType.getInteger(c,"row"),IntegerArgumentType.getInteger(c,"band"));
                        String json="ACCEPTANCE "+new Gson().toJson(value);
                        c.getSource().sendSuccess(() -> Component.literal(json),false);return 1;
                    }))))));
    }
    private static synchronized Map<String,Object> band(MinecraftServer server,int cx,int rz,int band) {
        if(Thread.currentThread().getName().equals("terrain-diffusion-inference"))throw new IllegalStateException("Blocking inference callback");
        try {
            WorldGeologySettings.current(server);
            long currentSeed=LocalTerrainProvider.getSeed();
            boolean miss=grid==null||owner!=server||seed!=currentSeed||col!=cx||row!=rz;
            if(miss) {
                grid=null;
                int x0=cx*256+128-1536,z0=rz*256+128-1536,n=3073;
                var values=LocalTerrainProvider.getPipelineData(z0,x0,z0+n,x0+n,false)[0];
                if(values.length!=n*n)throw new IllegalStateException("Patch shape");
                var hash=java.security.MessageDigest.getInstance("SHA-256");
                for(float v:values) {
                    if(!Float.isFinite(v))throw new IllegalStateException("Nonfinite patch");
                    int bits=Float.floatToIntBits(v);
                    for(int shift=24;shift>=0;shift-=8)hash.update((byte)(bits>>>shift));
                }
                float[][] next=new float[49][49];
                for(int r=0;r<49;r++)for(int k=0;k<49;k++)next[r][k]=values[(r*64)*n+k*64];
                WorldGeologySettings.current(server);
                grid=next;owner=server;seed=currentSeed;col=cx;row=rz;
                digest=HexFormat.of().formatHex(hash.digest());
            }
            return Map.of("col",cx,"row",rz,"band",band,"step_native_pixels",64,"radius_native_pixels",1536,
                "elevations",grid[band],"full_float_sha256",digest,"public_data_miss",miss,"patch_cache_entries",1);
        } catch(InterruptedException e) { Thread.currentThread().interrupt();grid=null;throw new IllegalStateException(e); }
        catch(Exception e) { grid=null;throw new IllegalStateException(e); }
    }
}
