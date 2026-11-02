package dev.wilyjeb.geology;
import com.github.xandergos.terraindiffusionmc.config.TerrainDiffusionConfig;
import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.github.xandergos.terraindiffusionmc.world.WorldScaleManager;
import dev.wilyjeb.geology.domain.Provinces;
import dev.wilyjeb.geology.domain.GeologySettings;
import dev.wilyjeb.geology.domain.Provinces.Stone;
import java.util.LinkedHashMap;
import java.util.Map;
/** Server worldgen API for future city palettes. Queries may perform terrain inference. */
public final class Geology {
    public record Region(Provinces.Province province, Stone stone, double elevationMetres, double reliefMetres) {}
    private record Key(net.minecraft.server.MinecraftServer server, long seed, int scale, GeologySettings settings, long x, long z) {}
    private static final Map<Key, Region> CACHE = new LinkedHashMap<>(512, 0.75f, true) {
        @Override protected boolean removeEldestEntry(Map.Entry<Key, Region> e) { return size() > 512; }
    };
    private Geology() {}
    public static Region regionAt(int x, int z) {
        return regionAt(WorldGeologySettings.server(), x, z);
    }
    public static Region regionAt(net.minecraft.server.MinecraftServer server, int x, int z) {
        if (server == null) throw new IllegalStateException("Geology settings are unavailable before a TD Overworld loads");
        try { return query(server, x, z); }
        catch (dev.wilyjeb.geology.domain.GeologyFailure failure) { throw failure; }
        catch (RuntimeException failure) { throw WorldGeologySettings.fail(server, "Geology query at " + x + ", " + z, failure); }
    }
    private static Region query(net.minecraft.server.MinecraftServer server, int x, int z) {
        var settings = WorldGeologySettings.current(server);
        long seed = LocalTerrainProvider.getSeed();
        int scale = WorldScaleManager.getCurrentScale();
        var province = Provinces.at(seed, scale, x, z, settings);
        var key = new Key(server, seed, scale, settings, province.cellX(), province.cellZ());
        synchronized (CACHE) { var found = CACHE.get(key); if (found != null) return found; }
        // TD's public accessors submit to its single executor and then wait.
        if (Thread.currentThread().getName().equals("terrain-diffusion-inference"))
            throw new IllegalStateException("A cold geology query cannot run on TD's inference thread");
        int tile = TerrainDiffusionConfig.tileSize();
        int sx = Math.floorDiv(province.anchorX(), tile) * tile;
        int sz = Math.floorDiv(province.anchorZ(), tile) * tile;
        // At native scale, handle1x's unpadded elevation is exactly pipeline.get(...)[0].
        // Geology needs neither climate/biomes nor the extra slope-padding request.
        // Keep the original path for upsampling: it adds scale-dependent elevation noise.
        short[][] heights;
        if (scale == 1) {
            try {
                var elevation = LocalTerrainProvider.getPipelineData(sz, sx, sz + tile, sx + tile, false)[0];
                heights = new short[5][5];
                for (int row = 0; row < 5; row++) for (int col = 0; col < 5; col++) {
                    float h = elevation[(row * (tile-1) / 4) * tile + col * (tile-1) / 4];
                    // Match TD's buildHeightmapData, including saturation and NaN conversion.
                    heights[row][col] = (short)Math.max(-32768, Math.min(32767, (int)Math.floor(h)));
                }
            } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException("Interrupted while sampling geology elevation", interrupted);
            } catch (Exception failure) {
                throw new IllegalStateException("Cannot sample geology elevation", failure);
            }
        } else {
            var data = LocalTerrainProvider.getInstance().fetchHeightmap(sz, sx, sz + tile, sx + tile);
            heights = new short[5][5];
            for (int row = 0; row < 5; row++) for (int col = 0; col < 5; col++)
                heights[row][col] = data.heightmap[row * (data.height-1) / 4][col * (data.width-1) / 4];
        }
        WorldGeologySettings.current(server); // Reject explorer edits and closed-world work after inference too.
        double sum = 0, low = Double.POSITIVE_INFINITY, high = Double.NEGATIVE_INFINITY;
        for (int row = 0; row < 5; row++) for (int col = 0; col < 5; col++) {
            double h = heights[row][col];
            sum += h; low = Math.min(low, h); high = Math.max(high, h);
        }
        double mean = sum / 25;
        var result = new Region(province, Provinces.classify(province, mean, high-low, settings), mean, high-low);
        synchronized (CACHE) { CACHE.put(key, result); }
        return result;
    }
    public static void clearCache() { synchronized (CACHE) { CACHE.clear(); } }
}
