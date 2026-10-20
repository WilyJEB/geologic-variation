package dev.wilyjeb.geology;

import com.github.xandergos.terraindiffusionmc.world.TerrainDiffusionBiomeSource;
import com.mojang.logging.LogUtils;
import dev.wilyjeb.geology.domain.GeologySettings;
import dev.wilyjeb.geology.domain.SettingsStore;
import java.io.IOException;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.LevelResource;
import net.neoforged.neoforge.event.level.LevelEvent;
import net.neoforged.fml.event.config.ModConfigEvent;

public final class WorldGeologySettings {
    private static final org.slf4j.Logger LOGGER = LogUtils.getLogger();
    private static volatile GeologySettings active;
    private static volatile dev.wilyjeb.geology.domain.GenerationContext context;
    private WorldGeologySettings() {}
    public static GeologySettings current() {
        var settings = active;
        if (settings == null) throw new IllegalStateException("Geology settings are unavailable before a TD Overworld loads");
        context.requireCompatible(TerrainGenerationContext.live(context));
        return settings;
    }
    public static void load(LevelEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !level.dimension().equals(Level.OVERWORLD)
                || !(level.getChunkSource().getGenerator().getBiomeSource() instanceof TerrainDiffusionBiomeSource)) return;
        var path = level.getServer().getWorldPath(LevelResource.ROOT).resolve("data/geologic_variation-geology.properties");
        try {
            clear();
            var runtime = TerrainGenerationContext.capture();
            if (runtime.seed() != level.getSeed()) throw new IllegalArgumentException("TD provider seed is not initialized for this world");
            var result = SettingsStore.loadOrCreate(path, GeologyConfig::requested,
                    level.getServer().getWorldData().overworldData().isInitialized(), runtime);
            context = runtime;
            active = result.settings();
            Geology.clearCache();
            LOGGER.info("Geologic Variation {} world settings at {}: {}",
                    result.created() ? "saved" : "loaded", path, active);
            if (result.adoptedLegacyDefaults()) LOGGER.info(
                    "Existing world has no geology snapshot; preserving legacy defaults instead of adopting edited config.");
            explainConfigDifference();
        } catch (IOException | IllegalArgumentException failure) {
            active = null;
            throw new IllegalStateException("Cannot initialize world geology settings: " + path, failure);
        }
    }
    public static void reloaded(ModConfigEvent.Reloading event) {
        if (event.getConfig().getSpec() == GeologyConfig.SPEC) explainConfigDifference();
    }
    private static void explainConfigDifference() {
        var snapshot = active;
        if (snapshot == null) return;
        try {
            if (!snapshot.equals(GeologyConfig.requested())) LOGGER.warn(
                    "Geology config differs from this world's snapshot. Saved world settings remain active; edits apply only to new worlds.");
        } catch (IllegalArgumentException invalid) {
            LOGGER.warn("Invalid requested geology config: {}. Saved world settings remain active.", invalid.getMessage());
        }
    }
    public static void clear() { active = null; context = null; Geology.clearCache(); }
}
