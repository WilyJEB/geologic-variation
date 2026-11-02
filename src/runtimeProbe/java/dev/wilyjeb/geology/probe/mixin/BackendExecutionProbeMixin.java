package dev.wilyjeb.geology.probe.mixin;

import com.github.xandergos.terraindiffusionmc.pipeline.OnnxModel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Passive completed-call evidence; never schedules or invokes inference. */
@Mixin(OnnxModel.class)
public abstract class BackendExecutionProbeMixin {
    @Inject(method = "run", at = @At("RETURN"), remap = false)
    private void probe$completed(Object[][] inputs, CallbackInfoReturnable<float[]> ci) {
        org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info(
                "TD_MODEL_RETURN provider={} outputs={} thread={}",
                OnnxModel.getResolvedInferenceProvider(), ci.getReturnValue().length,
                Thread.currentThread().getName());
    }
}
