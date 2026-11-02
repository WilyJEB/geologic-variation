package dev.wilyjeb.geology.probe;

import com.google.gson.Gson;
import com.github.xandergos.terraindiffusionmc.pipeline.LocalTerrainProvider;
import com.github.xandergos.terraindiffusionmc.explorer.ExplorerServer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.BackupConfirmScreen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.server.MinecraftServer;
import java.nio.file.*;
import java.util.*;

/** Explicitly enabled disposable-client file bridge. No production lifecycle calls are replaced. */
public final class IntegratedLifecycle {
    private static final Gson JSON = new Gson();
    private static boolean busy;
    private static MinecraftServer previous;
    private static final List<MinecraftServer> servers = new ArrayList<>();
    private static Path root() { return Minecraft.getInstance().gameDirectory.toPath(); }
    private static Object field(String type, String name) throws Exception {
        var f=Class.forName(type).getDeclaredField(name); f.setAccessible(true); return f.get(null);
    }
    public static void attach() {
        if (!Boolean.getBoolean("geology.acceptance.integrated")) return;
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(
            (net.neoforged.neoforge.event.server.ServerAboutToStartEvent e) -> {
                previous=e.getServer(); servers.add(previous);
                previous.tickRateManager().setFrozen(true);
                org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info("INTEGRATED_SERVER {}",servers.size());
            });
    }
    private static Map<String,Object> state() throws Exception {
        var mc=Minecraft.getInstance(); var result=new LinkedHashMap<String,Object>();
        result.put("pid",ProcessHandle.current().pid());
        result.put("screen",mc.screen==null?"none":mc.screen.getClass().getName());
        result.put("narration",mc.screen==null?"":mc.screen.getNarrationMessage().getString());
        result.put("joined",mc.player!=null && mc.level!=null);
        result.put("tick_frozen",mc.getSingleplayerServer()!=null && mc.getSingleplayerServer().tickRateManager().isFrozen());
        result.put("server_count",servers.size());
        result.put("server_ids",servers.stream().map(System::identityHashCode).toList());
        result.put("server_threads_alive",servers.stream().map(s->s.getRunningThread().isAlive()).toList());
        result.put("previous_shutdown",previous==null || previous.isShutdown());
        result.put("client_server_null",mc.getSingleplayerServer()==null);
        result.put("owner_null",field("dev.wilyjeb.geology.WorldGeologySettings","owner")==null);
        result.put("active_null",field("dev.wilyjeb.geology.WorldGeologySettings","active")==null);
        result.put("context_null",field("dev.wilyjeb.geology.WorldGeologySettings","context")==null);
        var cache=(Map<?,?>)field("dev.wilyjeb.geology.Geology","CACHE");
        synchronized(cache) { result.put("geology_cache",cache.size()); }
        result.put("td_pending",((Map<?,?>)field(LocalTerrainProvider.class.getName(),"PENDING")).size());
        result.put("td_cache",((Map<?,?>)field(LocalTerrainProvider.class.getName(),"CACHE")).size());
        result.put("td_seed",LocalTerrainProvider.getSeed());
        result.put("explorer_running",ExplorerServer.isRunning());
        result.put("explorer_port",ExplorerServer.getPort());
        result.put("td_threads",Thread.getAllStackTraces().keySet().stream().filter(t->t.getName().contains("terrain-") || t.getName().contains("HTTP-Dispatcher"))
            .map(t->Map.of("id",t.threadId(),"name",t.getName(),"daemon",t.isDaemon(),"state",t.getState().toString())).toList());
        return result;
    }
    private static void reply(Object value) throws Exception {
        Path tmp=root().resolve("bridge-response.tmp"); Files.writeString(tmp,JSON.toJson(value));
        Files.move(tmp,root().resolve("bridge-response.json"),StandardCopyOption.REPLACE_EXISTING);
    }
    public static void poll() {
        if (busy) return;
        var mc=Minecraft.getInstance();
        Path request=root().resolve("bridge-request.txt");
        if (!Files.exists(request)) return;
        busy=true;
        try {
            String command=Files.readString(request).strip(); Files.delete(request);
            String[] parts=command.split(" ",2);
            switch(parts[0]) {
                case "open" -> {
                    if (!Set.of("control","rejected").contains(parts[1])) throw new IllegalArgumentException("Unknown fixture");
                    mc.createWorldOpenFlows().openWorld(parts[1],()->mc.setScreen(new TitleScreen()));
                    reply(state());
                }
                case "confirm" -> {
                    if (!(mc.screen instanceof BackupConfirmScreen)) throw new IllegalStateException("Not a backup confirmation");
                    // Standard disposable-world experimental warning: Proceed, without creating another backup.
                    var button=mc.screen.children().stream().filter(x->x instanceof Button b && b.getMessage().getString().equals("Proceed"))
                        .map(x->(Button)x).findFirst().orElseThrow(); button.onPress(); reply(state());
                }
                case "state" -> reply(state());
                case "explorer" -> { ExplorerServer.startIfNotRunning(); reply(state()); }
                case "command" -> {
                    var server=mc.getSingleplayerServer();
                    if(server==null) throw new IllegalStateException("No integrated server");
                    server.submit(()-> {
                        server.getCommands().performPrefixedCommand(server.createCommandSourceStack(),parts[1]);
                        try { reply(Map.of("command",parts[1],"completed",true)); } catch(Exception e) { throw new RuntimeException(e); }
                    });
                }
                case "disconnect" -> {
                    // Match PauseScreen's normal disconnect sequence: the level closes the memory connection first.
                    if (mc.level!=null) mc.level.disconnect();
                    mc.disconnect(); mc.setScreen(new TitleScreen()); reply(state());
                }
                case "screenshot" -> {
                    net.minecraft.client.Screenshot.grab(mc.gameDirectory, "recovery.png", mc.getMainRenderTarget(), c -> {});
                    reply(state());
                }
                case "quit" -> { reply(state()); mc.stop(); }
                default -> throw new IllegalArgumentException(command);
            }
        } catch(Throwable e) {
            try { reply(Map.of("error",e.toString())); } catch(Exception ignored) {}
        } finally { busy=false; }
    }
}
