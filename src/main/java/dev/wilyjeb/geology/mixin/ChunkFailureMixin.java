package dev.wilyjeb.geology.mixin;

import dev.wilyjeb.geology.GeologyServer;
import net.minecraft.server.level.ChunkMap;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(ChunkMap.class)
public abstract class ChunkFailureMixin implements dev.wilyjeb.geology.GeologyChunks {
    @Shadow @Final private ServerLevel level;
    @Override public dev.wilyjeb.geology.domain.FailureState geology$failures() {
        return ((GeologyServer) level.getServer()).geology$failures();
    }

    // ServerChunkCache.close invokes this independently of MinecraftServer's save.
    @Inject(method = "saveAllChunks", at = @At("HEAD"), cancellable = true)
    private void geology$skipFlush(boolean flush, CallbackInfo ci) {
        if (((GeologyServer) level.getServer()).geology$failures().failure() != null) ci.cancel();
    }

    // Also cover individual autosaves and unload callbacks queued before failure.
    @Inject(method = "save", at = @At("HEAD"), cancellable = true)
    private void geology$skipChunk(ChunkAccess chunk, CallbackInfoReturnable<Boolean> ci) {
        if (((GeologyServer) level.getServer()).geology$failures().failure() != null) ci.setReturnValue(false);
    }
}
