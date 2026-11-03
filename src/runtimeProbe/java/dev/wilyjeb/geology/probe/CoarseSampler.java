package dev.wilyjeb.geology.probe;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.github.xandergos.terraindiffusionmc.pipeline.WorldPipelineModelConfig;
import com.github.xandergos.terraindiffusionmc.world.WorldScaleManager;
import dev.wilyjeb.geology.WorldGeologySettings;
import dev.wilyjeb.geology.domain.CoarseEvidence;
import java.util.*;
import net.minecraft.server.MinecraftServer;

/** Opt-in diagnostic. Bounded 3x3 halo and 128-entry LRU. No worldgen integration.
 * Serialized misses deduplicate concurrent callers; no inference-thread caller may
 * take the monitor, including a hit (prevents lock inversion with queued work).
 */
public final class CoarseSampler {
    private record Key(MinecraftServer owner, long seed, int scale, Object settings, int row, int col) {}
    private static final Map<Key,Map<String,Object>> CACHE = new LinkedHashMap<>(128,.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<Key,Map<String,Object>> e) { return size()>128; }
    };
    private CoarseSampler() {}
    public static Map<String,Object> measure(MinecraftServer server,String arm,int x,int z) {
        var before=Performance.metrics();long start=System.nanoTime();Object value;
        if(arm.equals("current"))value=dev.wilyjeb.geology.Geology.regionAt(server,x,z).toString();
        else if(arm.equals("coarse")) {
            var province=dev.wilyjeb.geology.domain.Provinces.at(LocalTerrainProvider.getSeed(),
                WorldScaleManager.getCurrentScale(),x,z,WorldGeologySettings.current(server));
            value=sample(server,province.anchorX(),province.anchorZ());
        } else throw new IllegalArgumentException("Unknown sampler");
        double ms=(System.nanoTime()-start)/1e6;var after=Performance.metrics();
        var delta=new LinkedHashMap<String,Long>();
        for(String key:before.keySet())delta.put(key,((Number)after.get(key)).longValue()-((Number)before.get(key)).longValue());
        return Map.of("arm",arm,"x",x,"z",z,"ms",ms,"delta",delta,"value",value);
    }
    public static void clear() { synchronized(CACHE) { CACHE.clear(); } }
    /** Compare identical province anchors. Diagnostic only; never select blocks. */
    public static Map<String,Object> comparison(MinecraftServer server,int x,int z) {
        var region=dev.wilyjeb.geology.Geology.regionAt(server,x,z);
        var p=region.province();
        return Map.of("x",x,"z",z,"province",Map.of("cell_x",p.cellX(),"cell_z",p.cellZ(),
            "anchor_x",p.anchorX(),"anchor_z",p.anchorZ(),"identity",p.identity()),
            "fine_mean_metres",region.elevationMetres(),"fine_tile_relief_metres",region.reliefMetres(),
            "geology_1_stone",region.stone().id(),"coarse",sample(server,p.anchorX(),p.anchorZ()));
    }
    public static Map<String,Object> suite(MinecraftServer server) throws Exception {
        int scale=WorldScaleManager.getCurrentScale(),stride=256*scale;
        clear();
        var pool=java.util.concurrent.Executors.newFixedThreadPool(4);
        long calls=Performance.COARSE.get();
        var futures=new ArrayList<java.util.concurrent.Future<Map<String,Object>>>();
        try {
            for(int i=0;i<4;i++) futures.add(pool.submit(() -> sample(server,-7*stride,11*stride)));
            var first=futures.getFirst().get();
            for(var f:futures)if(!first.equals(f.get()))throw new IllegalStateException("Concurrent disagreement");
        } finally { pool.shutdownNow(); }
        long concurrentCalls=Performance.COARSE.get()-calls;
        if(concurrentCalls!=1)throw new IllegalStateException("Miss not deduplicated");
        var points=new int[][]{{-stride-1,2*stride},{-stride,2*stride},{-1,0},{0,-1},{stride-1,-stride},{stride,-stride}};
        var forward=new ArrayList<Map<String,Object>>();
        for(var p:points)forward.add(sample(server,p[0],p[1]));
        clear();
        for(int i=points.length-1;i>=0;i--)if(!forward.get(i).equals(sample(server,points[i][0],points[i][1])))
            throw new IllegalStateException("Traversal disagreement");
        clear();
        for(int i=0;i<129;i++)sample(server,(i%16)*stride,(i/16)*stride);
        int size; synchronized(CACHE) { size=CACHE.size(); }
        calls=Performance.COARSE.get();sample(server,0,0);
        if(size!=128 || Performance.COARSE.get()-calls!=1)throw new IllegalStateException("LRU bound/eviction");
        return Map.of("concurrent_callers",4,"concurrent_requests",concurrentCalls,"traversal_equal",true,
            "boundary_points",forward,"real_cache_entries",size,"evicted_recomputed",true);
    }
    public static Map<String,Object> sample(MinecraftServer server,int x,int z) {
        if (Thread.currentThread().getName().equals("terrain-diffusion-inference"))
            throw new IllegalStateException("Coarse queries cannot run on TD inference thread");
        try {
            synchronized(CACHE) {
                // The production context guard runs before cache access and after inference.
                var settings=WorldGeologySettings.current(server);
                int scale=WorldScaleManager.getCurrentScale();
                if (WorldPipelineModelConfig.latentCompression()!=8 || WorldPipelineModelConfig.coarsePooling()!=1
                    || WorldPipelineModelConfig.nativeResolution()!=30
                    || !WorldPipelineModelConfig.elevCoarsePoolMode().equals("avg")
                    || !WorldPipelineModelConfig.p5CoarsePoolMode().equals("avg"))
                    throw new IllegalStateException("Unvalidated coarse model metadata");
                int row=CoarseEvidence.index(z,scale), col=CoarseEvidence.index(x,scale);
                var key=new Key(server,LocalTerrainProvider.getSeed(),scale,settings,row,col);
                var found=CACHE.get(key); if(found!=null) return found;
                var tensor=LocalTerrainProvider.getPipelineCoarse(row-1,col-1,row+2,col+2);
                if (!Arrays.equals(tensor.shape,new int[]{7,3,3}) || tensor.data.length!=63)
                    throw new IllegalStateException("Unexpected coarse tensor shape");
                var elevations=new ArrayList<Double>();
                double min=Double.POSITIVE_INFINITY,max=Double.NEGATIVE_INFINITY,sum=0;
                for(int i=0;i<9;i++) {
                    double h=CoarseEvidence.decode(tensor.data[i],tensor.data[54+i],0);
                    if(!Double.isFinite(h)) throw new IllegalStateException("Unavailable coarse elevation evidence");
                    elevations.add(h); min=Math.min(min,h);max=Math.max(max,h);sum+=h;
                }
                WorldGeologySettings.current(server);
                var value=Map.<String,Object>of("version",CoarseEvidence.VERSION,"row",row,"col",col,
                    "scale",scale,"elevations",List.copyOf(elevations),"mean_metres",sum/9,
                    "neighborhood_range_metres",max-min,"classification","unclassified evidence",
                    "p5_used",false);
                CACHE.put(key,value);return value;
            }
        } catch(InterruptedException e) { Thread.currentThread().interrupt();clear();throw new IllegalStateException(e); }
        catch(Exception e) { clear();throw new IllegalStateException(e); }
    }
    public static Map<String,Object> check(MinecraftServer server) throws Exception {
        // Asymmetric rectangle exposes swapped axes/flattening. Independent Explorer oracle.
        var method=Class.forName("com.github.xandergos.terraindiffusionmc.explorer.ExplorerServer")
            .getDeclaredMethod("coarseChannel",int.class,int.class,int.class,int.class,int.class);
        method.setAccessible(true);
        int row=-3,col=1,H=2,W=3;
        var raw=LocalTerrainProvider.getPipelineCoarse(row,col,row+H,col+W);
        if(!Arrays.equals(raw.shape,new int[]{7,H,W}))throw new IllegalStateException("Shape");
        for(int ch=0;ch<6;ch++) {
            float[] oracle=(float[])method.invoke(null,row,row+H,col,col+W,ch);
            for(int i=0;i<H*W;i++) {
                double actual=CoarseEvidence.decode(raw.data[ch*H*W+i],raw.data[6*H*W+i],ch);
                if(actual!=oracle[i])throw new IllegalStateException("Explorer mismatch");
            }
        }
        // Individual cells verify rectangle placement rather than just shared flattening.
        for(int r=0;r<H;r++)for(int c=0;c<W;c++) {
            var one=LocalTerrainProvider.getPipelineCoarse(row+r,col+c,row+r+1,col+c+1);
            for(int ch=0;ch<7;ch++) if(one.data[ch]!=raw.data[ch*H*W+r*W+c])
                throw new IllegalStateException("Coordinate/slice mismatch");
        }
        return Map.of("explorer_channels",6,"values",H*W*6,"single_cell_checks",6,
            "axis_order","row=z,column=x","native_stride",256,"equal",true);
    }
}
