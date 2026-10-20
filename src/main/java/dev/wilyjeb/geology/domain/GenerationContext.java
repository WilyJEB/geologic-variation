package dev.wilyjeb.geology.domain;

/** Exact compatibility identity, separate from the snapshot storage schema. */
public record GenerationContext(String generator, long seed, int scale, int tileSize,
        String dependency, String models, String backend) {
    public static final String GENERATOR = "geology-1";
    public GenerationContext {
        if (scale < 1 || scale > 6 || tileSize <= 0 || (tileSize & (tileSize - 1)) != 0)
            throw new IllegalArgumentException("Invalid generation scale/tile size");
        if (BackendIdentity.unresolved(backend))
            throw new IllegalArgumentException("Unresolved inference backend; restore a verified snapshot or use a new test world");
        for (String value : new String[]{generator, dependency, models, backend})
            if (value == null || value.isBlank() || value.equals("unknown"))
                throw new IllegalArgumentException("Unresolved generation context");
    }
    public void requireCompatible(GenerationContext runtime) {
        if (!generator.equals(GENERATOR) || !equals(runtime))
            throw new IllegalArgumentException("Incompatible geology generation context. Saved: " + this
                    + "; runtime: " + runtime + ". Restore the original generator, TD dependency/models/backend and world seed/scale/tile size; snapshot unchanged.");
    }
}
