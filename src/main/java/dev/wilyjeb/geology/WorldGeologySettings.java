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
    private static volatile net.minecraft.server.MinecraftServer owner;
    private WorldGeologySettings() {}
    public static net.minecraft.server.MinecraftServer server() { return owner; }
    public static GeologySettings current() {
        return current(owner);
    }
    public static GeologySettings current(net.minecraft.server.MinecraftServer server) {
        if (server != null) {
            var failure = ((GeologyServer) server).geology$failures().failure();
            if (failure != null) throw failure;
        }
        if (server != owner) throw new dev.wilyjeb.geology.domain.GeologyFailure("This geology query belongs to a closed world", null);
        var settings = active;
        if (settings == null) throw new IllegalStateException("Geology settings are unavailable before a TD Overworld loads");
        try { context.requireCompatible(TerrainGenerationContext.live(context)); }
        catch (RuntimeException failure) { throw fail(server, "Generation context changed", failure); }
        return settings;
    }
    public static void checkServerFailure() {
        var server = owner;
        if (server != null && server.isSameThread()) ((GeologyServer) server).geology$failures().check();
    }
    public static dev.wilyjeb.geology.domain.GeologyFailure fail(String operation, Throwable cause) {
        return fail(owner, operation, cause);
    }
    public static dev.wilyjeb.geology.domain.GeologyFailure fail(net.minecraft.server.MinecraftServer server,
            String operation, Throwable cause) {
        var failure = new dev.wilyjeb.geology.domain.GeologyFailure(
                operation + ": " + cause.getMessage()
                + "\nRestore this world's original addon, TD/models/backend, seed, scale and tile size. "
                + "Do not delete or edit its geology snapshot. See logs/latest.log for details.", cause);
        if (server != null) failure = ((GeologyServer) server).geology$failures().record(failure);
        Geology.clearCache();
        LOGGER.error("Geologic Variation is aborting this world: {}", failure.getMessage());
        return failure;
    }
    public static void load(LevelEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !level.dimension().equals(Level.OVERWORLD)
                || !(level.getChunkSource().getGenerator().getBiomeSource() instanceof TerrainDiffusionBiomeSource)) return;
        var path = level.getServer().getWorldPath(LevelResource.ROOT).resolve("data/geologic_variation-geology.properties");
        try {
            clear();
            owner = level.getServer();
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
        } catch (IOException | RuntimeException failure) {
            active = null;
            throw fail("Cannot initialize world geology settings at " + path, failure);
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
    public static void clear() { active = null; context = null; owner = null; Geology.clearCache(); }
}
