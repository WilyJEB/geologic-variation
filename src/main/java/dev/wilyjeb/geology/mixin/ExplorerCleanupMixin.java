package dev.wilyjeb.geology.mixin;

import com.github.xandergos.terraindiffusionmc.explorer.ExplorerServer;
import com.sun.net.httpserver.HttpServer;
import java.util.concurrent.ExecutorService;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** TD stops the listener but leaves its per-explorer executor for eventual GC cleanup. */
@Mixin(ExplorerServer.class)
public abstract class ExplorerCleanupMixin {
    @Redirect(method="stop", at=@At(value="INVOKE", target="Lcom/sun/net/httpserver/HttpServer;stop(I)V"), remap=false)
    private static void geology$closeExecutor(HttpServer server, int delay) {
        var executor=server.getExecutor();
        try { server.stop(delay); }
        finally {
            if (executor instanceof ExecutorService service) service.shutdownNow();
        }
    }
}
