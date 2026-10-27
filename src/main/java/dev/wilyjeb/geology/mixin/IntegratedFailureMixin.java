package dev.wilyjeb.geology.mixin;

import dev.wilyjeb.geology.domain.GeologyFailure;
import net.minecraft.CrashReport;
import net.minecraft.client.server.IntegratedServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(IntegratedServer.class)
public abstract class IntegratedFailureMixin {
    @Inject(method = "onServerCrash", at = @At("HEAD"), cancellable = true)
    private void geology$recoverable(CrashReport report, CallbackInfo ci) {
        if (GeologyFailure.find(report.getException()) != null) {
            ((dev.wilyjeb.geology.GeologyClient) net.minecraft.client.Minecraft.getInstance())
                    .geology$recover((IntegratedServer) (Object) this);
            ci.cancel();
        }
    }
}
