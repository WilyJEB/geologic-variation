package dev.wilyjeb.geology.mixin;

import dev.wilyjeb.geology.GeologyServer;
import dev.wilyjeb.geology.domain.GeologyFailure;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.DisconnectedScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class ClientFailureMixin implements dev.wilyjeb.geology.GeologyClient {
    @Shadow private IntegratedServer singleplayerServer;
    @Unique private boolean geology$loading;
    @Unique private volatile IntegratedServer geology$failedServer;
    @Override public void geology$recover(IntegratedServer server) { geology$failedServer = server; }

    @Unique private GeologyFailure geology$finishedFailure() {
        var server = geology$failedServer != null ? geology$failedServer : singleplayerServer;
        return server != null && !server.getRunningThread().isAlive()
                ? ((GeologyServer) server).geology$failures().failure() : null;
    }

    @Inject(method = "doWorldLoad", at = @At("HEAD"))
    private void geology$loading(CallbackInfo ci) { geology$loading = true; }

    @Inject(method = "doWorldLoad", at = @At("RETURN"))
    private void geology$loaded(CallbackInfo ci) { geology$loading = false; }

    @Redirect(method = "doWorldLoad", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/server/IntegratedServer;isReady()Z"))
    private boolean geology$endLoadingWait(IntegratedServer server) {
        return server.isReady() || geology$finishedFailure() != null;
    }

    // This point is after the wait profiler section and before opening a connection.
    @Inject(method = "doWorldLoad", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/server/IntegratedServer;getConnection()Lnet/minecraft/server/network/ServerConnectionListener;"),
            cancellable = true)
    private void geology$abortConnection(CallbackInfo ci) {
        var failure = geology$finishedFailure();
        if (failure != null) {
            geology$loading = false;
            geology$showFailure(failure);
            ci.cancel();
        }
    }

    @Inject(method = "tick", at = @At("HEAD"))
    private void geology$activeWorldFailure(CallbackInfo ci) {
        if (!geology$loading) {
            var failure = geology$finishedFailure();
            if (failure != null) geology$showFailure(failure);
        }
    }

    @Unique private void geology$showFailure(GeologyFailure failure) {
        geology$failedServer = null;
        var minecraft = (Minecraft) (Object) this;
        minecraft.disconnect();
        minecraft.setScreen(new DisconnectedScreen(new TitleScreen(),
                Component.literal("Geologic Variation stopped this world"),
                Component.literal(failure.userMessage()), Component.translatable("gui.toTitle")));
    }
}
