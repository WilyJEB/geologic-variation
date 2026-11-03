package dev.wilyjeb.geology.probe;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.github.xandergos.terraindiffusionmc.world.WorldScaleManager;
import dev.wilyjeb.geology.WorldGeologySettings;
import dev.wilyjeb.geology.domain.Provinces;
import java.util.*;
import net.minecraft.server.MinecraftServer;

/** Evidence only. No production caller, fitted cutoffs, p5 or rock selection. */
public final class SamplingDiagnostic {
    private record Key(MinecraftServer server,long seed,int row,int col) {}
    private static final Map<Key,Map<String,Object>> FINE = new LinkedHashMap<>(128,.75f,true) {
        protected boolean removeEldestEntry(Map.Entry<Key,Map<String,Object>> e) { return size()>128; }
    };
    private SamplingDiagnostic() {}
    public static void clear() { synchronized(FINE) { FINE.clear(); } CoarseSampler.clear(); }
    private static Map<String,Object> nativeCell(MinecraftServer server,int row,int col) throws Exception {
        synchronized(FINE) {
            WorldGeologySettings.current(server);
            var key=new Key(server,LocalTerrainProvider.getSeed(),row,col);
            var found=FINE.get(key); if(found!=null)return found;
            // Native pipeline coordinates, independently of Minecraft world scale.
            var values=LocalTerrainProvider.getPipelineData(row*256,col*256,(row+1)*256,(col+1)*256,false)[0];
            if(values.length!=65536)throw new IllegalStateException("Native cell support");
            double sum=0,lo=Double.POSITIVE_INFINITY,hi=Double.NEGATIVE_INFINITY;int wet=0;
            var digest=java.security.MessageDigest.getInstance("SHA-256");
            for(float v:values) {
                if(!Float.isFinite(v))throw new IllegalStateException("Unavailable fine elevation");
                sum+=v;lo=Math.min(lo,v);hi=Math.max(hi,v);if(v<0)wet++;
                int bits=Float.floatToIntBits(v);
                for(int shift=24;shift>=0;shift-=8)digest.update((byte)(bits>>>shift));
            }
            WorldGeologySettings.current(server);
            var result=Map.<String,Object>of("row",row,"col",col,"samples",values.length,
                "mean_metres",sum/values.length,"fine_cell_relief_metres",hi-lo,
                "below_zero_fraction",wet/(double)values.length,"float_sha256",HexFormat.of().formatHex(digest.digest()));
            FINE.put(key,result);return result;
        }
    }
    private static Map<String,Object> tile(MinecraftServer server,int x,int z) throws Exception {
        int sx=Math.floorDiv(x,256)*256,sz=Math.floorDiv(z,256)*256;
        double sum=0,lo=Double.POSITIVE_INFINITY,hi=Double.NEGATIVE_INFINITY;var heights=new ArrayList<Integer>();
        if(WorldScaleManager.getCurrentScale()==1) {
            var values=LocalTerrainProvider.getPipelineData(sz,sx,sz+256,sx+256,false)[0];
            for(int r=0;r<5;r++)for(int c=0;c<5;c++)heights.add((int)(short)Math.max(-32768,Math.min(32767,(int)Math.floor(values[(r*255/4)*256+c*255/4]))));
        } else {
            var data=LocalTerrainProvider.getInstance().fetchHeightmap(sz,sx,sz+256,sx+256);
            for(int r=0;r<5;r++)for(int c=0;c<5;c++)heights.add((int)data.heightmap[r*(data.height-1)/4][c*(data.width-1)/4]);
        }
        for(int v:heights){sum+=v;lo=Math.min(lo,v);hi=Math.max(hi,v);}
        WorldGeologySettings.current(server);
        return Map.of("x0",sx,"z0",sz,"width_blocks",256,"samples",heights,"mean_metres",sum/25,
            "fine_tile_relief_metres",hi-lo);
    }
    public static Map<String,Object> compare(MinecraftServer server,int x,int z) {
        if(Thread.currentThread().getName().equals("terrain-diffusion-inference"))throw new IllegalStateException("Blocking inference callback");
        try {
            var before=Performance.metrics();
            var settings=WorldGeologySettings.current(server);int scale=WorldScaleManager.getCurrentScale(),stride=256*scale;
            var p=Provinces.at(LocalTerrainProvider.getSeed(),scale,x,z,settings);
            int gx=(Math.floorDiv(x,4*stride)*4+2)*stride,gz=(Math.floorDiv(z,4*stride)*4+2)*stride;
            var policies=new LinkedHashMap<String,Object>();
            int[][] points={{p.anchorX(),p.anchorZ()},{x,z},{gx,gz}};
            String[] names={"province_anchor","target","fixed_grid_4"};
            for(int i=0;i<3;i++) {
                int px=points[i][0],pz=points[i][1];var coarse=CoarseSampler.sample(server,px,pz);
                policies.put(names[i],Map.of("x",px,"z",pz,"coarse",coarse,
                    "matched_native_cell",nativeCell(server,Math.floorDiv(pz,stride),Math.floorDiv(px,stride))));
            }
            var result=new LinkedHashMap<String,Object>();
            result.put("x",x);result.put("z",z);result.put("province",Map.of("identity",p.identity(),"anchor_x",p.anchorX(),"anchor_z",p.anchorZ()));
            result.put("policies",policies);result.put("target_fine_tile",tile(server,x,z));
            result.put("anchor_fine_tile",tile(server,p.anchorX(),p.anchorZ()));
            var after=Performance.metrics();var delta=new LinkedHashMap<String,Long>();
            for(String k:before.keySet())delta.put(k,((Number)after.get(k)).longValue()-((Number)before.get(k)).longValue());
            result.put("delta",delta);result.put("fine_cache_entries",FINE.size());return result;
        } catch(InterruptedException e){Thread.currentThread().interrupt();clear();throw new IllegalStateException(e);}
        catch(Exception e){clear();throw new IllegalStateException(e);}
    }
}
