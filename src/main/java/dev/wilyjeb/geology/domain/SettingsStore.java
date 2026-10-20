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

    public static synchronized Loaded loadOrCreate(Path path, Supplier<GeologySettings> requested,
            boolean existingWorld) throws IOException {
        if (Files.exists(path)) return new Loaded(read(path), false, false);
        // Pre-settings worlds have already generated with the legacy defaults. Never adopt edited config there.
        GeologySettings settings = existingWorld ? GeologySettings.DEFAULT : requested.get();
        Files.createDirectories(path.toAbsolutePath().getParent());
        Path temp = Files.createTempFile(path.toAbsolutePath().getParent(), "geology-", ".tmp");
        try {
            try (var output = Files.newOutputStream(temp)) {
                properties(settings).store(output, "Geologic Variation world snapshot; schema is the storage format only");
            }
            try (var channel = FileChannel.open(temp, StandardOpenOption.WRITE)) { channel.force(true); }
            try { Files.move(temp, path, StandardCopyOption.ATOMIC_MOVE); }
            catch (AtomicMoveNotSupportedException unsupported) { Files.move(temp, path); }
        } finally { Files.deleteIfExists(temp); }
        return new Loaded(settings, true, existingWorld);
    }
    public static GeologySettings read(Path path) throws IOException {
        if (Files.size(path) > 65536) throw new IOException("Geology settings snapshot exceeds 64 KiB: " + path);
        var values = new Properties();
        try {
            try (var input = Files.newInputStream(path)) { values.load(input); }
            if (!values.stringPropertyNames().equals(KEYS)) throw new IllegalArgumentException("missing or unknown fields");
            if (!"1".equals(values.getProperty("schema"))) throw new IllegalArgumentException("unsupported settings storage schema");
            return new GeologySettings(Integer.parseInt(values.getProperty("provinceSpacingBlocks")),
                    Double.parseDouble(values.getProperty("oceanCeilingMetres")),
                    Double.parseDouble(values.getProperty("lowlandCeilingMetres")),
                    Double.parseDouble(values.getProperty("mountainFloorMetres")),
                    Double.parseDouble(values.getProperty("gentleReliefMetres")),
                    Double.parseDouble(values.getProperty("ruggedReliefMetres")));
        } catch (IllegalArgumentException invalid) {
            throw new IOException("Invalid geology snapshot at " + path + ": " + invalid.getMessage()
                    + ". Restore the original snapshot; it will not be replaced with defaults.", invalid);
        }
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
