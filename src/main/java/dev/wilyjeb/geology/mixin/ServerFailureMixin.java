package dev.wilyjeb.geology.mixin;

import dev.wilyjeb.geology.GeologyServer;
import dev.wilyjeb.geology.WorldGeologySettings;
import dev.wilyjeb.geology.domain.FailureState;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(MinecraftServer.class)
public abstract class ServerFailureMixin implements GeologyServer {
    @Unique private final FailureState geology$state = new FailureState();
    @Override public FailureState geology$failures() { return geology$state; }

    // Both the spawn wait and ServerChunkCache's managed wait call this hook.
    // Do not use vanilla's process-global fatalException: it poisons later worlds.
    @Inject(method = "throwIfFatalException", at = @At("HEAD"))
    private static void geology$wakeWaits(CallbackInfoReturnable<Boolean> ci) {
        WorldGeologySettings.checkServerFailure();
    }

    @Inject(method = "setFatalException", at = @At("HEAD"), cancellable = true)
    private static void geology$keepFailureLocal(RuntimeException error, CallbackInfo ci) {
        if (dev.wilyjeb.geology.domain.GeologyFailure.find(error) != null) ci.cancel();
    }

    @Inject(method = "stopServer", at = @At("HEAD"))
    private void geology$stopping(CallbackInfo ci) { geology$state.stopping(); }

    @Redirect(method = "stopServer", at = @At(value = "FIELD",
            target = "Lnet/minecraft/server/level/ServerLevel;noSave:Z", opcode = 181))
    private void geology$preserveChunks(ServerLevel level, boolean noSave) {
        level.noSave = noSave || geology$state.failure() != null;
    }

    // Failed generation futures need not become ready for saving. Do not drain
    // the normal save/unload loop after disabling saves; still close resources.
    @Redirect(method = "stopServer", at = @At(value = "INVOKE",
            target = "Ljava/util/stream/Stream;anyMatch(Ljava/util/function/Predicate;)Z"))
    private boolean geology$skipFailedDrain(java.util.stream.Stream<ServerLevel> levels,
            java.util.function.Predicate<? super ServerLevel> hasWork) {
        return geology$state.failure() == null && levels.anyMatch(hasWork);
    }

    @Inject(method = "saveAllChunks", at = @At("HEAD"), cancellable = true)
    private void geology$skipFailedSave(boolean suppressLog, boolean flush, boolean forced,
            CallbackInfoReturnable<Boolean> ci) {
        if (geology$state.failure() != null) ci.setReturnValue(false);
    }
}
