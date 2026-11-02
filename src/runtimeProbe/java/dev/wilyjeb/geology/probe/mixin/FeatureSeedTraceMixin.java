package dev.wilyjeb.geology.probe.mixin;

import dev.wilyjeb.geology.probe.CoalTrace;
import net.minecraft.world.level.levelgen.WorldgenRandom;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(WorldgenRandom.class)
public abstract class FeatureSeedTraceMixin {
    @Inject(method="setFeatureSeed",at=@At("RETURN"))
    private void trace$seed(long decorationSeed,int featureIndex,int step,CallbackInfo ci) {
        CoalTrace.featureSeed(decorationSeed,featureIndex,step);
    }
}
