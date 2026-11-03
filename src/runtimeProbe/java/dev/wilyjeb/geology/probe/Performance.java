package dev.wilyjeb.geology.probe;

import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;

/** Passive counters only: never schedules inference from an inference callback. */
public final class Performance {
    public static final AtomicLong HEIGHTMAP = new AtomicLong();
    public static final AtomicLong ANCHOR = new AtomicLong();
    public static final AtomicLong DATA = new AtomicLong();
    public static final AtomicLong COARSE = new AtomicLong();
    private Performance() {}
    /** Same JVM, warm tensor windows, empty provider heightmap cache in both arms.
     * Measures only accessor + exact 25-value extraction, not full chunk generation. */
    public static Map<String,Object> compare(int x,int z) {
        check(x,z); // Prime both paths and verify every elevation, outside timing.
        int tile=com.github.xandergos.terraindiffusionmc.config.TerrainDiffusionConfig.tileSize();
        x=Math.floorDiv(x,tile)*tile; z=Math.floorDiv(z,tile)*tile;
        long before=((Number)metrics().get("computed_windows")).longValue();
        var pairs=new java.util.ArrayList<Map<String,Object>>();
        for(int trial=-3;trial<20;trial++) {
            var pair=new java.util.LinkedHashMap<String,Object>();
            long[] fingerprint=new long[2];
            for(int step=0;step<2;step++) {
                boolean original=(step==0)==(trial%2==0);
                LocalTerrainProvider.clearCache();
                long start=System.nanoTime();
                long sum=0;
                if(original) {
                    var data=LocalTerrainProvider.getInstance().fetchHeightmap(z,x,z+tile,x+tile);
                    for(int row=0;row<5;row++) for(int col=0;col<5;col++)
                        sum=31*sum+data.heightmap[row*(tile-1)/4][col*(tile-1)/4];
                } else {
                    try {
                        var data=LocalTerrainProvider.getPipelineData(z,x,z+tile,x+tile,false)[0];
                        for(int row=0;row<5;row++) for(int col=0;col<5;col++) {
                            short value=(short)Math.max(-32768,Math.min(32767,(int)Math.floor(data[(row*(tile-1)/4)*tile+col*(tile-1)/4])));
                            sum=31*sum+value;
                        }
                    } catch(Exception e) { throw new RuntimeException(e); }
                }
                pair.put(original?"old_ms":"new_ms",(System.nanoTime()-start)/1e6);
                fingerprint[original?0:1]=sum;
            }
            if(fingerprint[0]!=fingerprint[1]) throw new IllegalStateException("Sampler mismatch");
            if(trial>=0) pairs.add(pair);
        }
        long windows=((Number)metrics().get("computed_windows")).longValue()-before;
        if(windows!=0) throw new IllegalStateException("Expected already-warm tensor windows");
        return Map.of("x",x,"z",z,"warmup_pairs",3,"pairs",pairs,"computed_windows",windows,"equal",true);
    }
    public static Map<String,Object> check(int x, int z) {
        try {
            if (com.github.xandergos.terraindiffusionmc.world.WorldScaleManager.getCurrentScale() != 1)
                throw new IllegalStateException("Native scale only");
            int tile = com.github.xandergos.terraindiffusionmc.config.TerrainDiffusionConfig.tileSize();
            x = Math.floorDiv(x,tile)*tile; z = Math.floorDiv(z,tile)*tile;
            var raw = LocalTerrainProvider.getPipelineData(z,x,z+tile,x+tile,false)[0];
            var original = LocalTerrainProvider.getInstance().fetchHeightmap(z,x,z+tile,x+tile);
            var digest = java.security.MessageDigest.getInstance("SHA-256");
            for (int row=0; row<tile; row++) for (int col=0; col<tile; col++) {
                short expected = (short)Math.max(-32768,Math.min(32767,(int)Math.floor(raw[row*tile+col])));
                if (expected != original.heightmap[row][col]) throw new IllegalStateException("Elevation mismatch");
                digest.update((byte)(expected >>> 8)); digest.update((byte)expected);
            }
            return Map.of("x",x,"z",z,"equal",true,"samples",tile*tile,
                    "sha256",java.util.HexFormat.of().formatHex(digest.digest()));
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    public static Map<String,Object> metrics() {
        try {
            var field = LocalTerrainProvider.class.getDeclaredField("pipeline");
            field.setAccessible(true);
            var pipeline = (com.github.xandergos.terraindiffusionmc.pipeline.WorldPipeline)
                    field.get(LocalTerrainProvider.getInstance());
            return Map.of("heightmap_calls", HEIGHTMAP.get(), "anchor_heightmap_calls", ANCHOR.get(),
                    "pipeline_data_calls", DATA.get(), "coarse_calls", COARSE.get(), "computed_windows", pipeline.getTotalComputedWindowCount());
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }
}
