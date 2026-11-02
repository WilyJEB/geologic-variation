package dev.wilyjeb.geology.probe;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.commands.CommandSourceStack;
import net.neoforged.fml.ModList;
import net.neoforged.fml.event.config.ModConfigEvent;

/** Passive observer of the addon's real mod-bus events; never dispatches reloads. */
public final class HotConfig {
    private static final List<Map<String,Object>> EVENTS = new ArrayList<>();
    private static boolean attached;
    private HotConfig() {}
    public static synchronized void attach() {
        if (attached) return;
        ModList.get().getModContainerById("geologic_variation").ifPresent(container -> {
            container.getEventBus().addListener(net.neoforged.bus.api.EventPriority.LOWEST, HotConfig::reloaded);
            attached = true;
        });
    }
    private static void reloaded(ModConfigEvent.Reloading event) {
        if (!event.getConfig().getModId().equals("geologic_variation")) return;
        try {
            Class<?> config = Class.forName("dev.wilyjeb.geology.GeologyConfig");
            Map<String,Object> result = new LinkedHashMap<>();
            result.put("event", event.getClass().getName());
            result.put("type", event.getConfig().getType().name());
            result.put("file", event.getConfig().getFileName());
            result.put("spec_matches", event.getConfig().getSpec() == config.getField("SPEC").get(null));
            result.put("requested", config.getMethod("requested").invoke(null).toString());
            result.put("thread", Thread.currentThread().getName());
            result.put("watcher_stack", StackWalker.getInstance().walk(frames -> frames.anyMatch(
                f -> f.getClassName().equals("net.neoforged.fml.config.ConfigWatcher") && f.getMethodName().equals("run"))));
            synchronized (EVENTS) { EVENTS.add(Map.copyOf(result)); }
            org.slf4j.LoggerFactory.getLogger("GeologyRuntimeProbe").info("HOT_CONFIG {}",new com.google.gson.Gson().toJson(result));
        } catch (ReflectiveOperationException failure) { throw new RuntimeException(failure); }
    }
    public static Map<String,Object> events() {
        synchronized (EVENTS) { return Map.of("kind","reload-events","events",List.copyOf(EVENTS)); }
    }
    public static Map<String,Object> cache(CommandSourceStack source, String action) {
        if (!List.of("clear","query").contains(action)) throw new IllegalArgumentException("Expected clear|query");
        try {
            Class<?> geology = Class.forName("dev.wilyjeb.geology.Geology");
            var field = geology.getDeclaredField("CACHE"); field.setAccessible(true);
            Map<?,?> cache = (Map<?,?>) field.get(null);
            Map<String,Object> result = new LinkedHashMap<>();
            result.put("kind","reload-cache"); result.put("action",action);
            synchronized(cache) { result.put("entries_before",cache.size()); }
            long calls = LiveContext.HEIGHTMAP_CALLS.get();
            if (action.equals("clear")) geology.getMethod("clearCache").invoke(null);
            else result.put("region",geology.getMethod("regionAt",net.minecraft.server.MinecraftServer.class,int.class,int.class)
                .invoke(null,source.getServer(),-508,-1027).toString());
            synchronized(cache) { result.put("entries_after",cache.size()); }
            result.put("heightmap_calls",LiveContext.HEIGHTMAP_CALLS.get()-calls);
            result.put("thread",Thread.currentThread().getName());
            return result;
        } catch (ReflectiveOperationException failure) { throw new RuntimeException(failure); }
    }
}
