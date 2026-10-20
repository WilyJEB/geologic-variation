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
    private record Key(long seed, int scale, GeologySettings settings, long x, long z) {}
    private static final Map<Key, Region> CACHE = new LinkedHashMap<>(512, 0.75f, true) {
        @Override protected boolean removeEldestEntry(Map.Entry<Key, Region> e) { return size() > 512; }
    };
    private Geology() {}
    public static Region regionAt(int x, int z) {
        var settings = WorldGeologySettings.current();
        long seed = LocalTerrainProvider.getSeed();
        int scale = WorldScaleManager.getCurrentScale();
        var province = Provinces.at(seed, scale, x, z, settings);
        var key = new Key(seed, scale, settings, province.cellX(), province.cellZ());
        synchronized (CACHE) { var found = CACHE.get(key); if (found != null) return found; }
        int tile = TerrainDiffusionConfig.tileSize();
        int sx = Math.floorDiv(province.anchorX(), tile) * tile;
        int sz = Math.floorDiv(province.anchorZ(), tile) * tile;
        var data = LocalTerrainProvider.getInstance().fetchHeightmap(sz, sx, sz + tile, sx + tile);
        WorldGeologySettings.current(); // Reject explorer seed/scale edits made during inference too.
        double sum = 0, low = Double.POSITIVE_INFINITY, high = Double.NEGATIVE_INFINITY;
        for (int row = 0; row < 5; row++) for (int col = 0; col < 5; col++) {
            double h = data.heightmap[row * (data.height-1) / 4][col * (data.width-1) / 4];
            sum += h; low = Math.min(low, h); high = Math.max(high, h);
        }
        double mean = sum / 25;
        var result = new Region(province, Provinces.classify(province, mean, high-low, settings), mean, high-low);
        synchronized (CACHE) { CACHE.put(key, result); }
        return result;
    }
    public static void clearCache() { synchronized (CACHE) { CACHE.clear(); } }
}
