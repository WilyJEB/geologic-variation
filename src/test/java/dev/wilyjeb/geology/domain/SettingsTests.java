package dev.wilyjeb.geology.domain;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Comparator;

public final class SettingsTests {
    private static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
    private static void invalid(Runnable action) {
        try { action.run(); throw new AssertionError("Expected invalid settings rejection"); }
        catch (IllegalArgumentException expected) {}
    }
    @FunctionalInterface private interface IoAction { void run() throws IOException; }
    private static void unreadable(IoAction action) {
        try { action.run(); throw new AssertionError("Expected snapshot rejection"); }
        catch (IOException expected) {}
    }
 public static long fingerprint(GeologySettings settings) {
  long hash=1;
  for (long seed : new long[]{0,42,-987654321}) for (int scale=1;scale<=6;scale++)
   for (int x=-50000;x<=50000;x+=991) {
    var p=Provinces.at(seed,scale,x,-x+117,settings);
    hash=hash*31+p.cellX(); hash=hash*31+p.cellZ();
    hash=hash*31+p.anchorX(); hash=hash*31+p.anchorZ(); hash=hash*31+p.identity();
    for(double h : new double[]{-800,-200,100,600,1000,1800,3000})
     for(double r : new double[]{0,100,300,600,900}) hash=hash*31+Provinces.classify(p,h,r,settings).ordinal();
   }
  return hash;
 }

    public static void main(String[] args) throws IOException {
        var defaults = GeologySettings.DEFAULT;
        check(fingerprint(defaults) == -4340957394944646000L,
                "Default province anchors and classification changed from the pre-settings build");
        var tuned = new GeologySettings(4096, 500, 1000, 2500, 1000, 2000);
        check(fingerprint(tuned) != fingerprint(defaults), "Settings do not affect generation");
        check(new GeologySettings(256,-10000,0,10000,0,20000).provinceSpacingBlocks() == 256, "lower bound");
        new GeologySettings(65536,-10000,0,10000,0,20000);
        invalid(() -> new GeologySettings(255,-200,600,1800,300,600));
        invalid(() -> new GeologySettings(65537,-200,600,1800,300,600));
        invalid(() -> new GeologySettings(2048,600,600,1800,300,600));
        invalid(() -> new GeologySettings(2048,-200,1800,600,300,600));
        invalid(() -> new GeologySettings(2048,Double.NaN,600,1800,300,600));
        invalid(() -> new GeologySettings(2048,-200,600,Double.POSITIVE_INFINITY,300,600));
        invalid(() -> new GeologySettings(2048,-200,600,1800,-1,600));
        invalid(() -> new GeologySettings(2048,-200,600,1800,600,600));
        invalid(() -> new GeologySettings(2048,-200,600,1800,300,20001));
        invalid(() -> new GeologySettings(2048,-200,600,1800,Double.NaN,600));
        invalid(() -> new GeologySettings(2048,-10001,600,1800,300,600));
        Path fixture = Files.createTempDirectory(Path.of("build").toAbsolutePath(), "settings-tests-");
        try {
            Path world = fixture.resolve("new-world/data/settings.properties");
            var first = SettingsStore.loadOrCreate(world, () -> tuned, false);
            check(first.created() && !first.adoptedLegacyDefaults() && first.settings().equals(tuned), "new-world config snapshot");
            byte[] original = Files.readAllBytes(world);
            var reopened = SettingsStore.loadOrCreate(world, () -> defaults, true);
            check(!reopened.created() && reopened.settings().equals(tuned), "config edit changed a continuing world");
            check(fingerprint(reopened.settings()) == fingerprint(tuned), "reload changed world generation");
            check(Arrays.equals(original, Files.readAllBytes(world)), "reload rewrote world settings");
            SettingsStore.loadOrCreate(world, () -> { throw new AssertionError("Existing snapshot consulted config"); }, true);
            var legacy = SettingsStore.loadOrCreate(fixture.resolve("legacy.properties"),
                    () -> { throw new AssertionError("Legacy world adopted edited config"); }, true);
            check(legacy.created() && legacy.adoptedLegacyDefaults() && legacy.settings().equals(defaults), "legacy adoption");
            var other = SettingsStore.loadOrCreate(fixture.resolve("other-world.properties"), () -> defaults, false);
            check(other.settings().equals(defaults) && SettingsStore.read(world).equals(tuned), "world settings leaked between worlds");
            Path invalid = fixture.resolve("invalid.properties");
            for (String broken : new String[]{"", "schema=99", new String(original).replace("schema=1", "schema=2"),
                    new String(original).replace("provinceSpacingBlocks=4096", "provinceSpacingBlocks=0"),
                    new String(original).replace("oceanCeilingMetres=500.0", "oceanCeilingMetres=NaN"),
                    new String(original) + "unexpected=1\n", "bad=" + (char)92 + "uZZZZ"}) {
                Files.writeString(invalid, broken);
                unreadable(() -> SettingsStore.loadOrCreate(invalid, () -> defaults, true));
                check(Files.readString(invalid).equals(broken), "Invalid snapshot was overwritten");
            }
            Files.writeString(invalid, "x".repeat(65537));
            unreadable(() -> SettingsStore.read(invalid));
            Path badParent = fixture.resolve("file-parent");
            Files.writeString(badParent, "not a directory");
            unreadable(() -> SettingsStore.loadOrCreate(badParent.resolve("settings.properties"), () -> defaults, false));
        } finally {
            try (var paths = Files.walk(fixture)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
                    if (!path.toAbsolutePath().normalize().startsWith(fixture.toAbsolutePath().normalize()))
                        throw new AssertionError("Cleanup escaped test fixture");
                    Files.delete(path);
                }
            }
        }
        System.out.println("Settings validation, pre-change generation fingerprint, persistence, config-edit isolation, legacy adoption, world isolation and corruption rejection passed.");
    }
}
