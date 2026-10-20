package dev.wilyjeb.geology;

import dev.wilyjeb.geology.domain.GeologySettings;
import net.neoforged.neoforge.common.ModConfigSpec;

/** Common config proposes settings for new TD worlds; a continuing world uses its own snapshot. */
public final class GeologyConfig {
    public static final ModConfigSpec SPEC;
    private static final ModConfigSpec.IntValue SPACING;
    private static final ModConfigSpec.DoubleValue OCEAN, LOWLAND, MOUNTAIN, GENTLE, RUGGED;
    static {
        var b = new ModConfigSpec.Builder();
        b.comment("Settings for NEW Terrain Diffusion worlds only. Continuing worlds keep their saved snapshot.",
                "Elevation thresholds must satisfy ocean < lowland < mountain; relief must satisfy gentle < rugged.").push("geology");
        SPACING = b.comment("Province anchor spacing in Minecraft blocks at TD scale 1; multiplied by world scale (1..6).")
                .defineInRange("provinceSpacingBlocks", 2048, 256, 65536);
        OCEAN = b.comment("Deep-ocean classification ceiling, TD metres.")
                .defineInRange("oceanCeilingMetres", -200.0, -10000.0, 10000.0);
        LOWLAND = b.comment("Lowland classification ceiling, TD metres.")
                .defineInRange("lowlandCeilingMetres", 600.0, -10000.0, 10000.0);
        MOUNTAIN = b.comment("High-terrain classification floor, TD metres.")
                .defineInRange("mountainFloorMetres", 1800.0, -10000.0, 10000.0);
        GENTLE = b.comment("Gentle terrain relief ceiling: maximum minus minimum anchor sample elevation, TD metres.")
                .defineInRange("gentleReliefMetres", 300.0, 0.0, 20000.0);
        RUGGED = b.comment("Rugged terrain relief floor, TD metres.")
                .defineInRange("ruggedReliefMetres", 600.0, 0.0, 20000.0);
        b.pop(); SPEC = b.build();
    }
    private GeologyConfig() {}
    public static GeologySettings requested() {
        return new GeologySettings(SPACING.get(), OCEAN.get(), LOWLAND.get(), MOUNTAIN.get(), GENTLE.get(), RUGGED.get());
    }
}
