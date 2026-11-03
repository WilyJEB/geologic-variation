package dev.wilyjeb.geology.domain;

/** Experimental evidence codec only; never supplies geology-1 classification. */
public final class CoarseEvidence {
    public static final String VERSION = "coarse-evidence-1";
    public static final int NATIVE_STRIDE = 256;
    private CoarseEvidence() {}
    public static int index(int block, int scale) {
        if (scale < 1 || scale > 6) throw new IllegalArgumentException("Unsupported scale");
        return Math.floorDiv(block, NATIVE_STRIDE * scale);
    }
    /** Input is already denormalized by TD; divide blend weight exactly once.
     * Missing evidence stays missing, including nonfinite weights/signals.
     * Use float division to match Explorer, then signed square in double precision.
     */
    public static double decode(float weighted, float weight, int channel) {
        if (channel < 0 || channel > 5) throw new IllegalArgumentException("Unknown channel");
        if (!Float.isFinite(weight) || weight <= 1e-8f || !Float.isFinite(weighted)) return Double.NaN;
        float raw = weighted / weight;
        if (!Float.isFinite(raw)) return Double.NaN;
        return channel <= 1 ? (float)(Math.signum(raw) * (double)raw * raw) : raw;
    }
}
