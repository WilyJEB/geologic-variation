package dev.wilyjeb.geology.probe;

import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.github.xandergos.terraindiffusionmc.world.WorldScaleManager;
import net.minecraft.commands.CommandSourceStack;

/** Test-only atomic edit/query on the server command thread; never TD's inference thread. */
public final class LiveContext {
    public static final AtomicLong HEIGHTMAP_CALLS = new AtomicLong();
    private LiveContext() {}
    public static int run(CommandSourceStack source, String field, String route) {
        if (!java.util.Set.of("seed","scale").contains(field) || !java.util.Set.of("cached","uncached").contains(route))
            throw new IllegalArgumentException("Expected seed|scale cached|uncached");
        try {
            Class<?> geology=Class.forName("dev.wilyjeb.geology.Geology");
            var query=geology.getMethod("regionAt",net.minecraft.server.MinecraftServer.class,int.class,int.class);
            geology.getMethod("clearCache").invoke(null);
            String expected=query.invoke(null,source.getServer(),-508,-1027).toString();
            var cacheField=geology.getDeclaredField("CACHE");cacheField.setAccessible(true);
            Map<?,?> cache=(Map<?,?>)cacheField.get(null);
            int warm;
            synchronized(cache) { warm=cache.size(); }
            if(warm!=1)throw new IllegalStateException("Expected one real cached province");
            if(route.equals("uncached"))geology.getMethod("clearCache").invoke(null);
            int entries;
            synchronized(cache) { entries=cache.size(); }
            long seed=LocalTerrainProvider.getSeed(); int scale=WorldScaleManager.getCurrentScale();
            long calls=HEIGHTMAP_CALLS.get();
            long dataCalls=Performance.DATA.get();
            // Exact public API used by ExplorerServer / world scale management in pinned TD.
            if(field.equals("seed"))LocalTerrainProvider.changeSeedFromExplorer(seed+1);
            else WorldScaleManager.setCurrentScale(source.getServer().overworld(),6);
            Throwable rejected=null;
            try { query.invoke(null,source.getServer(),-508,-1027); }
            catch(java.lang.reflect.InvocationTargetException failure) { rejected=failure.getCause(); }
            var result=new java.util.LinkedHashMap<String,Object>();
            result.put("kind","live-context");result.put("field",field);result.put("route",route);
            result.put("thread",Thread.currentThread().getName());result.put("expected_region",expected);
            result.put("cache_entries_before_edit",entries);result.put("seed_before",seed);result.put("scale_before",scale);
            result.put("seed_after",LocalTerrainProvider.getSeed());result.put("scale_after",WorldScaleManager.getCurrentScale());
            result.put("heightmap_calls_after_edit",HEIGHTMAP_CALLS.get()-calls);
            result.put("pipeline_data_calls_after_edit",Performance.DATA.get()-dataCalls);
            result.put("rejected",rejected!=null);result.put("diagnostic",rejected==null?"QUERY RETURNED":rejected.toString());
            synchronized(cache) { result.put("cache_entries_after",cache.size()); }
            org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info("LIVE_CONTEXT {}",new com.google.gson.Gson().toJson(result));
            if(rejected==null)throw new IllegalStateException("Incompatible query returned");
            return 1;
        } catch(Exception failure) { throw new RuntimeException(failure); }
    }
}
