package dev.wilyjeb.geology.domain;

import java.io.IOException;
import java.util.function.Supplier;

/** TD loads model bytes before its lazy first inference selects a provider. */
public final class BackendIdentity {
    @FunctionalInterface public interface Initializer { void run() throws IOException; }
    private BackendIdentity() {}
    public static String resolve(Supplier<String> provider, Initializer initialize) throws IOException {
        String value = provider.get();
        if (unresolved(value)) {
            initialize.run();
            value = provider.get();
        }
        if (unresolved(value)) throw new IOException("TD inference provider is still unresolved after initialization; no geology snapshot will be saved");
        return value;
    }
    public static boolean unresolved(String value) {
        return value == null || value.isBlank() || value.equalsIgnoreCase("unknown")
                || value.regionMatches(true, 0, "unknown/", 0, 8);
    }
}
