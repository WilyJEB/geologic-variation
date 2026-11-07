package dev.wilyjeb.geology.probe.mixin;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import dev.wilyjeb.geology.probe.NumericalSupport;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Optional bit capture without changing the frozen diagnostic's source bytes. */
@Mixin(LocalTerrainProvider.class)
public abstract class NumericalCaptureMixin {
    @Inject(method="getPipelineData",at=@At("RETURN"),remap=false)
    private static void probe$capture(int z0,int x0,int z1,int x1,boolean climate,
            CallbackInfoReturnable<float[][]> ci) {
        try { NumericalSupport.captureNative(Math.floorDiv(z0,256),Math.floorDiv(x0,256),ci.getReturnValue()[0]); }
        catch(Exception e) { throw new IllegalStateException(e); }
    }
}
