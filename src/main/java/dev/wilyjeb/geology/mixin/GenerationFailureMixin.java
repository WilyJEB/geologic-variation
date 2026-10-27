package dev.wilyjeb.geology.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import dev.wilyjeb.geology.GeologyChunks;
import dev.wilyjeb.geology.domain.GeologyFailure;
import java.util.concurrent.CompletableFuture;
import net.minecraft.server.level.ChunkResult;
import net.minecraft.server.level.GeneratingChunkMap;
import net.minecraft.server.level.GenerationChunkHolder;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.chunk.status.ChunkStep;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

@Mixin(GenerationChunkHolder.class)
public abstract class GenerationFailureMixin {
    @Shadow private CompletableFuture<ChunkResult<ChunkAccess>> getOrCreateFuture(ChunkStatus status) {
        throw new AssertionError("Mixin shadow");
    }

    // Do not let a tagged ReportedException escape the worker: vanilla's worker
    // uncaught handler calls System.exit. Complete the status as a failed result
    // so dependent generation tasks cancel and release their claims normally.
    @WrapMethod(method = "applyStep")
    private CompletableFuture<ChunkResult<ChunkAccess>> geology$cancelFailedGeneration(
            ChunkStep step, GeneratingChunkMap chunks, StaticCache2D<GenerationChunkHolder> cache,
            Operation<CompletableFuture<ChunkResult<ChunkAccess>>> original) {
        if (!(chunks instanceof GeologyChunks geologyChunks)) return original.call(step, chunks, cache);
        var state = geologyChunks.geology$failures();
        var failure = state.failure();
        boolean threwDuringStep = false;
        if (failure == null) {
            try { return original.call(step, chunks, cache); }
            catch (RuntimeException error) {
                failure = GeologyFailure.find(error);
                if (failure == null) throw error;
                threwDuringStep = true;
            }
        }
        var result = ChunkResult.<ChunkAccess>error(failure::userMessage);
        // Only complete the status we acquired and failed synchronously. A
        // different already-running step may still own an asynchronous success.
        if (threwDuringStep) getOrCreateFuture(step.targetStatus()).complete(result);
        return CompletableFuture.completedFuture(result);
    }
}
