package dev.wilyjeb.geology.probe.mixin;

import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class IntegratedClientProbeMixin {
    @Inject(method="tick", at=@At("RETURN"))
    private void acceptance$poll(CallbackInfo ci) {
        if (Boolean.getBoolean("geology.acceptance.integrated"))
            dev.wilyjeb.geology.probe.IntegratedLifecycle.poll();
    }
}
