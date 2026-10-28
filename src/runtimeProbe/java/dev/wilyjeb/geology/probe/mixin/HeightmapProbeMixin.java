package dev.wilyjeb.geology.probe.mixin;

import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Request wall time, including cache/queue wait; explicitly not inference CPU time. */
@Mixin(LocalTerrainProvider.class)
public abstract class HeightmapProbeMixin {
    private static final ThreadLocal<Long> probe$start = new ThreadLocal<>();
    private static final ThreadLocal<String> probe$caller = new ThreadLocal<>();

    @Inject(method = "fetchHeightmap", at = @At("HEAD"), remap = false)
    private void probe$begin(int z0, int x0, int z1, int x1, CallbackInfoReturnable<Object> ci) {
        String caller = StackWalker.getInstance().walk(frames -> frames
                .anyMatch(frame -> frame.getClassName().equals("dev.wilyjeb.geology.Geology")))
                ? "addon-anchor" : "td-or-other";
        probe$caller.set(caller);
        probe$start.set(System.nanoTime());
    }

    @Inject(method = "fetchHeightmap", at = @At("RETURN"), remap = false)
    private void probe$end(int z0, int x0, int z1, int x1, CallbackInfoReturnable<Object> ci) {
        double ms = (System.nanoTime() - probe$start.get()) / 1e6;
        // Avoid logging every cache hit; totals are available from the chunk/region commands.
        if (ms >= 1) org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info(
                "TD_REQUEST caller={} x={} z={} width={} height={} wall_ms={}",
                probe$caller.get(), x0, z0, x1-x0, z1-z0, ms);
        probe$start.remove();
        probe$caller.remove();
    }
}
