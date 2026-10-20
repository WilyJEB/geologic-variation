package dev.wilyjeb.geology.domain;

/** Immutable world settings. Elevation/relief use TD metres; spacing uses blocks at scale 1. */
public record GeologySettings(int provinceSpacingBlocks, double oceanCeilingMetres,
        double lowlandCeilingMetres, double mountainFloorMetres,
        double gentleReliefMetres, double ruggedReliefMetres) {
    public static final GeologySettings DEFAULT = new GeologySettings(2048, -200, 600, 1800, 300, 600);
    public GeologySettings {
        if (provinceSpacingBlocks < 256 || provinceSpacingBlocks > 65536)
            throw new IllegalArgumentException("provinceSpacingBlocks must be 256..65536");
        for (double value : new double[]{oceanCeilingMetres, lowlandCeilingMetres, mountainFloorMetres})
            if (!Double.isFinite(value) || value < -10000 || value > 10000)
                throw new IllegalArgumentException("elevation thresholds must be finite and within -10000..10000 metres");
        if (!(oceanCeilingMetres < lowlandCeilingMetres && lowlandCeilingMetres < mountainFloorMetres))
            throw new IllegalArgumentException("elevation thresholds must satisfy ocean < lowland < mountain");
        if (!Double.isFinite(gentleReliefMetres) || !Double.isFinite(ruggedReliefMetres)
                || gentleReliefMetres < 0 || ruggedReliefMetres > 20000 || gentleReliefMetres >= ruggedReliefMetres)
            throw new IllegalArgumentException("relief thresholds must satisfy 0 <= gentle < rugged <= 20000 metres");
    }
}
