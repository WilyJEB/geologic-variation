package dev.wilyjeb.geology.domain;

import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.StandardOpenOption;
import java.util.Properties;
import java.util.Set;
import java.util.function.Supplier;

/** One snapshot per world. Minecraft's world lock provides exclusive process ownership. */
public final class SettingsStore {
    private static final Set<String> KEYS = Set.of("schema", "provinceSpacingBlocks", "oceanCeilingMetres",
            "lowlandCeilingMetres", "mountainFloorMetres", "gentleReliefMetres", "ruggedReliefMetres");
    public record Loaded(GeologySettings settings, boolean created, boolean adoptedLegacyDefaults) {}
    private SettingsStore() {}

    /** Contextless worlds cannot be upgraded by guessing their previous inference inputs. */
    public static synchronized Loaded loadOrCreate(Path path, Supplier<GeologySettings> requested,
            boolean existingWorld, GenerationContext runtime) throws IOException {
        runtime.requireCompatible(runtime);
        if (Files.exists(path)) {
            var values = readProperties(path);
            if (!"2".equals(values.getProperty("schema")))
                throw new IOException("Unverified legacy geology context at " + path
                        + ". Keep the original installation and snapshot; explicit provenance migration is required.");
            try {
                var context = new GenerationContext(values.getProperty("generator"),
                        Long.parseLong(values.getProperty("seed")), Integer.parseInt(values.getProperty("scale")),
                        Integer.parseInt(values.getProperty("tileSize")), values.getProperty("dependency"),
                        values.getProperty("models"), values.getProperty("backend"));
                context.requireCompatible(runtime);
                for (String key : Set.of("generator", "seed", "scale", "tileSize", "dependency", "models", "backend"))
                    values.remove(key);
                values.setProperty("schema", "1");
                return new Loaded(parse(values), false, false);
            } catch (IllegalArgumentException invalid) {
                throw new IOException("Cannot continue geology at " + path + ": " + invalid.getMessage(), invalid);
            }
        }
        if (existingWorld) throw new IOException("Existing world has no verified geology context at " + path
                + ". Restore its original installation; automatic context adoption is unsafe.");
        var settings = requested.get();
        var values = properties(settings);
        values.setProperty("schema", "2");
        values.setProperty("generator", runtime.generator());
        values.setProperty("seed", Long.toString(runtime.seed()));
        values.setProperty("scale", Integer.toString(runtime.scale()));
        values.setProperty("tileSize", Integer.toString(runtime.tileSize()));
        values.setProperty("dependency", runtime.dependency());
        values.setProperty("models", runtime.models());
        values.setProperty("backend", runtime.backend());
        write(path, values);
        return new Loaded(settings, true, false);
    }

    /** Legacy schema-1 fixture codec; runtime callers must supply a GenerationContext. */
    static synchronized Loaded loadOrCreate(Path path, Supplier<GeologySettings> requested,
            boolean existingWorld) throws IOException {
        if (Files.exists(path)) return new Loaded(read(path), false, false);
        // Pre-settings worlds have already generated with the legacy defaults. Never adopt edited config there.
        GeologySettings settings = existingWorld ? GeologySettings.DEFAULT : requested.get();
        write(path, properties(settings));
        return new Loaded(settings, true, existingWorld);
    }
    private static void write(Path path, Properties values) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        Path temp = Files.createTempFile(path.toAbsolutePath().getParent(), "geology-", ".tmp");
        try {
            try (var output = Files.newOutputStream(temp)) {
                values.store(output, "Geologic Variation world snapshot; preserve with world backups");
            }
            try (var channel = FileChannel.open(temp, StandardOpenOption.WRITE)) { channel.force(true); }
            try { Files.move(temp, path, StandardCopyOption.ATOMIC_MOVE); }
            catch (AtomicMoveNotSupportedException unsupported) { Files.move(temp, path); }
        } finally { Files.deleteIfExists(temp); }
    }
    public static GeologySettings read(Path path) throws IOException {
        try { return parse(readProperties(path)); }
        catch (IllegalArgumentException invalid) { throw new IOException("Invalid geology snapshot at " + path, invalid); }
    }
    private static Properties readProperties(Path path) throws IOException {
        if (Files.size(path) > 65536) throw new IOException("Geology settings snapshot exceeds 64 KiB: " + path);
        var values = new Properties();
        try {
            try (var input = Files.newInputStream(path)) { values.load(input); }
            return values;
        } catch (IllegalArgumentException invalid) { throw new IOException("Invalid geology snapshot at " + path, invalid); }
    }
    private static GeologySettings parse(Properties values) {
            if (!values.stringPropertyNames().equals(KEYS)) throw new IllegalArgumentException("missing or unknown fields");
            if (!"1".equals(values.getProperty("schema"))) throw new IllegalArgumentException("unsupported settings storage schema");
            return new GeologySettings(Integer.parseInt(values.getProperty("provinceSpacingBlocks")),
                    Double.parseDouble(values.getProperty("oceanCeilingMetres")),
                    Double.parseDouble(values.getProperty("lowlandCeilingMetres")),
                    Double.parseDouble(values.getProperty("mountainFloorMetres")),
                    Double.parseDouble(values.getProperty("gentleReliefMetres")),
                    Double.parseDouble(values.getProperty("ruggedReliefMetres")));
    }
    private static Properties properties(GeologySettings settings) {
        var values = new Properties();
        values.setProperty("schema", "1");
        values.setProperty("provinceSpacingBlocks", Integer.toString(settings.provinceSpacingBlocks()));
        values.setProperty("oceanCeilingMetres", Double.toString(settings.oceanCeilingMetres()));
        values.setProperty("lowlandCeilingMetres", Double.toString(settings.lowlandCeilingMetres()));
        values.setProperty("mountainFloorMetres", Double.toString(settings.mountainFloorMetres()));
        values.setProperty("gentleReliefMetres", Double.toString(settings.gentleReliefMetres()));
        values.setProperty("ruggedReliefMetres", Double.toString(settings.ruggedReliefMetres()));
        return values;
    }
}
