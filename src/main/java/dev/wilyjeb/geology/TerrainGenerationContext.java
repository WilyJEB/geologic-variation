package dev.wilyjeb.geology;

import com.github.xandergos.terraindiffusionmc.config.TerrainDiffusionConfig;
import com.github.xandergos.terraindiffusionmc.pipeline.*;
import com.github.xandergos.terraindiffusionmc.world.WorldScaleManager;
import com.google.gson.JsonParser;
import dev.wilyjeb.geology.domain.GenerationContext;
import dev.wilyjeb.geology.domain.BackendIdentity;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import net.neoforged.fml.ModList;

final class TerrainGenerationContext {
    private TerrainGenerationContext() {}
    static GenerationContext capture() throws IOException {
        PipelineModels.awaitLoad();
        String provider = BackendIdentity.resolve(OnnxModel::getResolvedInferenceProvider, () -> {
            com.mojang.logging.LogUtils.getLogger().info("Resolving TD inference provider before saving geology context...");
            try {
                // The public accessor serializes work on TD's inference thread. One coarse
                // sample forces its lazy provider selection without generating Minecraft chunks.
                LocalTerrainProvider.getPipelineCoarse(0, 0, 1, 1);
            } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                throw new IOException("Interrupted while resolving TD inference provider", interrupted);
            } catch (Exception failure) {
                throw new IOException("Cannot resolve TD inference provider; snapshot not saved", failure);
            }
        });
        var assets = new StringBuilder();
        try (var input = ModelAssetManager.class.getResourceAsStream("/model-assets-manifest.json")) {
            if (input == null) throw new IOException("TD model manifest unavailable");
            var manifest = JsonParser.parseString(new String(input.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8))
                    .getAsJsonObject().getAsJsonObject("assets");
            for (String name : manifest.keySet().stream().sorted().toList())
                assets.append(name).append('=').append(hash(ModelAssetManager.resolveAssetPath(name))).append(';');
        }
        var dependency = ModList.get().getModFileById("terrain_diffusion_mc").getFile().getFilePath();
        return new GenerationContext(GenerationContext.GENERATOR, LocalTerrainProvider.getSeed(),
                WorldScaleManager.getCurrentScale(), TerrainDiffusionConfig.tileSize(), hash(dependency),
                HexFormat.of().formatHex(digest().digest(assets.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8))),
                provider + "/" + System.getProperty("os.name")
                        + "/" + System.getProperty("os.arch"));
    }
    static GenerationContext live(GenerationContext saved) {
        return new GenerationContext(GenerationContext.GENERATOR, LocalTerrainProvider.getSeed(),
                WorldScaleManager.getCurrentScale(), TerrainDiffusionConfig.tileSize(), saved.dependency(),
                saved.models(), OnnxModel.getResolvedInferenceProvider() + "/" + System.getProperty("os.name")
                        + "/" + System.getProperty("os.arch"));
    }
    private static MessageDigest digest() {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
    }
    private static String hash(Path path) throws IOException {
        var hash = digest();
        try (var input = Files.newInputStream(path)) {
            byte[] buffer = new byte[1024 * 1024];
            for (int count; (count = input.read(buffer)) != -1;) hash.update(buffer, 0, count);
        }
        return HexFormat.of().formatHex(hash.digest());
    }
}
