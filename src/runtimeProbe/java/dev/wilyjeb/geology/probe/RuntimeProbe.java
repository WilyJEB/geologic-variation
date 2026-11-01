package dev.wilyjeb.geology.probe;

import com.google.gson.Gson;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.Level;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.Executors;

@Mod("geology_runtime_probe")
public final class RuntimeProbe {
    public RuntimeProbe() { NeoForge.EVENT_BUS.addListener(RuntimeProbe::commands); }
    private static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("acceptance").requires(s -> s.hasPermission(4))
            .then(Commands.literal("prepare").executes(c -> prepare(c.getSource())))
            .then(Commands.literal("cache-policy").executes(c -> cachePolicy(c.getSource())))
            .then(Commands.literal("chunk").then(Commands.argument("dimension", com.mojang.brigadier.arguments.StringArgumentType.word())
                .then(Commands.argument("x", IntegerArgumentType.integer()).then(Commands.argument("z", IntegerArgumentType.integer())
                    .executes(c -> chunk(c.getSource(), com.mojang.brigadier.arguments.StringArgumentType.getString(c,"dimension"),
                        IntegerArgumentType.getInteger(c,"x"), IntegerArgumentType.getInteger(c,"z")))))))
            .then(Commands.literal("region").then(Commands.argument("x", IntegerArgumentType.integer())
                .then(Commands.argument("z", IntegerArgumentType.integer()).executes(c -> region(c.getSource(),
                    IntegerArgumentType.getInteger(c,"x"),IntegerArgumentType.getInteger(c,"z"), false)))))
            .then(Commands.literal("concurrent").then(Commands.argument("x", IntegerArgumentType.integer())
                .then(Commands.argument("z", IntegerArgumentType.integer()).executes(c -> region(c.getSource(),
                    IntegerArgumentType.getInteger(c,"x"),IntegerArgumentType.getInteger(c,"z"), true))))));
    }
    private static int send(CommandSourceStack source, Map<String,Object> result) {
        String json = new Gson().toJson(result);
        org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info("ACCEPTANCE {}",json);
        source.sendSuccess(() -> Component.literal("ACCEPTANCE " + json),false);
        return 1;
    }
    private static int prepare(CommandSourceStack source) {
        try {
            com.github.xandergos.terraindiffusionmc.pipeline.PipelineModels.awaitLoad();
            com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider.getPipelineCoarse(0,0,1,1);
            return send(source, Map.of("kind","prepare", "processors",Runtime.getRuntime().availableProcessors(),
                    "max_heap",Runtime.getRuntime().maxMemory(), "backend",
                    com.github.xandergos.terraindiffusionmc.pipeline.OnnxModel.getResolvedInferenceProvider()));
        } catch(Exception e) { throw new RuntimeException(e); }
    }
    /** Exercise the real map's eviction policy without computing 600 remote terrain tiles.
     * Synthetic keys/values are confined to this frozen disposable server and always cleared.
     */
    @SuppressWarnings({"unchecked", "rawtypes"})
    private static int cachePolicy(CommandSourceStack source) {
        try {
            Class<?> geology=Class.forName("dev.wilyjeb.geology.Geology");
            var field=geology.getDeclaredField("CACHE");field.setAccessible(true);
            Map cache=(Map)field.get(null);
            synchronized(cache) {
                if(cache.isEmpty())throw new IllegalStateException("Query a real region first");
                Object original=cache.keySet().iterator().next(), value=cache.get(original);
                var type=original.getClass();
                var constructor=type.getDeclaredConstructors()[0];constructor.setAccessible(true);
                var components=type.getRecordComponents();
                Object[] args=new Object[components.length];
                for(int i=0;i<args.length;i++) {
                    var accessor=components[i].getAccessor();accessor.setAccessible(true);args[i]=accessor.invoke(original);
                }
                var keys=new java.util.ArrayList<Object>();
                try {
                    cache.clear();
                    for(int i=0;i<600;i++) {
                        args[args.length-2]=(long)i-1000000;
                        args[args.length-1]=-1000000L;
                        Object key=constructor.newInstance(args);keys.add(key);cache.put(key,value);
                        if(i==511)cache.get(keys.getFirst()); // One repeatedly visited province stays hot.
                        if(cache.size()>512)throw new IllegalStateException("Cache exceeded capacity");
                    }
                    boolean lru=cache.size()==512 && cache.containsKey(keys.getFirst())
                            && !cache.containsKey(keys.get(1)) && cache.containsKey(keys.getLast());
                    if(!lru)throw new IllegalStateException("LRU retention failed");
                    return send(source,Map.of("kind","cache-policy","synthetic_keys",600,"entries",cache.size(),"lru",true));
                } finally { cache.clear(); }
            }
        }catch(Exception e){throw new RuntimeException(e);}
    }
    private static int chunk(CommandSourceStack source, String dimension, int x, int z) {
        try {
            var level = source.getServer().getLevel(ResourceKey.create(Registries.DIMENSION,
                    ResourceLocation.parse("minecraft:"+dimension)));
            if (level == null) throw new IllegalArgumentException("Missing dimension");
            long start = System.nanoTime();
            var chunk = level.getChunk(x,z);
            double generationMs = (System.nanoTime()-start)/1e6;
            var digest = MessageDigest.getInstance("SHA-256");
            var geologyDigest = MessageDigest.getInstance("SHA-256");
            var counts = new java.util.TreeMap<String,Integer>();
            var pos = new BlockPos.MutableBlockPos();
            for (int y=chunk.getMinBuildHeight();y<chunk.getMaxBuildHeight();y++)
                for (int dz=0;dz<16;dz++) for (int dx=0;dx<16;dx++) {
                    pos.set(x*16+dx,y,z*16+dz);
                    var state=chunk.getBlockState(pos);
                    String id=BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();
                    digest.update((state.toString()+"\n").getBytes(StandardCharsets.UTF_8));
                    counts.merge(id,1,Integer::sum);
                    if (id.startsWith("geologic_variation:")) geologyDigest.update(
                        (dx+","+y+","+dz+":"+id+"\n").getBytes(StandardCharsets.UTF_8));
                }
            Map<String,Object> result=new LinkedHashMap<>();
            result.put("kind","chunk"); result.put("dimension",dimension); result.put("x",x);result.put("z",z);
            result.put("generation_ms",generationMs);result.put("blocks_sha256",HexFormat.of().formatHex(digest.digest()));
            result.put("geology_sha256",HexFormat.of().formatHex(geologyDigest.digest()));result.put("counts",counts);
            return send(source,result);
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    private static int region(CommandSourceStack source, int x, int z, boolean concurrent) {
        try {
            Class<?> geology=Class.forName("dev.wilyjeb.geology.Geology");
            var method=geology.getMethod("regionAt",net.minecraft.server.MinecraftServer.class,int.class,int.class);
            long start=System.nanoTime();
            String value;
            if (concurrent) {
                try (var pool=Executors.newFixedThreadPool(4)) {
                    var calls=new java.util.ArrayList<java.util.concurrent.Callable<String>>();
                    for(int i=0;i<4;i++) calls.add(() -> method.invoke(null,source.getServer(),x,z).toString());
                    var results=pool.invokeAll(calls);
                    value=results.getFirst().get();
                    for(var r:results) if(!value.equals(r.get()))throw new IllegalStateException("Concurrent mismatch");
                }
            } else value=method.invoke(null,source.getServer(),x,z).toString();
            Map<String,Object> result=new LinkedHashMap<>();result.put("kind",concurrent?"concurrent":"region");
            result.put("x",x);result.put("z",z);result.put("wall_ms",(System.nanoTime()-start)/1e6);result.put("region",value);
            var field=geology.getDeclaredField("CACHE");field.setAccessible(true);
            var cache=(Map<?,?>)field.get(null);
            synchronized(cache){result.put("cache_entries",cache.size());}
            result.put("addon_origin",geology.getProtectionDomain().getCodeSource().getLocation().toString());
            return send(source,result);
        }catch(Exception e){throw new RuntimeException(e);}
    }
}
