package dev.wilyjeb.geology.probe.mixin;

import com.github.xandergos.terraindiffusionmc.pipeline.WorldPipelineModelConfig;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Passive observation after TD has parsed and validated its real config. No inference. */
@Mixin(WorldPipelineModelConfig.class)
public abstract class ModelConfigProbeMixin {
    @Inject(method = "<clinit>", at = @At("TAIL"), remap = false)
    private static void probe$loaded(CallbackInfo ci) {
        org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info(
                "TD_MODEL_CONFIG residual_mean={} native_resolution={} latent_compression={}",
                WorldPipelineModelConfig.residualMean(), WorldPipelineModelConfig.nativeResolution(),
                WorldPipelineModelConfig.latentCompression());
    }
}
