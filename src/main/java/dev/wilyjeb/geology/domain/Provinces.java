package dev.wilyjeb.geology.domain;

/** Pure immutable province partition. Version 1 is a worldgen contract. */
public final class Provinces {
    /** Host layer, not a claim about the depth at which a rock formed. */
    public enum Layer { SURFACE, DEEP }
    public enum Stone {
        LIMESTONE(Layer.SURFACE), SLATE(Layer.SURFACE),
        QUARTZITE(Layer.SURFACE), GABBRO(Layer.SURFACE);
        private final Layer layer;
        Stone(Layer layer) { this.layer = layer; }
        public Layer layer() { return layer; }
        public String id() { return name().toLowerCase(java.util.Locale.ROOT); }
    }
    public record Province(long cellX, long cellZ, int anchorX, int anchorZ, long identity) {}
    private Provinces() {}
    public static long mix(long n) {
        n = (n ^ (n >>> 30)) * 0xbf58476d1ce4e5b9L;
        n = (n ^ (n >>> 27)) * 0x94d049bb133111ebL;
        return n ^ (n >>> 31);
    }
    private static double unit(long n) { return (mix(n) >>> 11) * 0x1.0p-53; }
    public static Province at(long seed, int scale, int x, int z) {
        return at(seed, scale, x, z, GeologySettings.DEFAULT);
    }
    public static Province at(long seed, int scale, int x, int z, GeologySettings settings) {
        if (scale < 1 || scale > 6) throw new IllegalArgumentException("scale must be 1..6");
        int spacing = settings.provinceSpacingBlocks() * scale;
        long cx = Math.floorDiv(x, spacing), cz = Math.floorDiv(z, spacing);
        Province best = null;
        double distance = Double.POSITIVE_INFINITY;
        for (long dz = -1; dz <= 1; dz++) for (long dx = -1; dx <= 1; dx++) {
            long gx = cx + dx, gz = cz + dz;
            long id = mix(seed ^ mix(gx) ^ Long.rotateLeft(mix(gz), 29));
            int ax = (int)Math.floor((gx + 0.25 + unit(id) * 0.5) * spacing);
            int az = (int)Math.floor((gz + 0.25 + unit(id ^ 0x72bdL) * 0.5) * spacing);
            double d = ((double)x-ax)*(x-ax) + ((double)z-az)*(z-az);
            if (d < distance) { distance = d; best = new Province(gx, gz, ax, az, id); }
        }
        return best;
    }
    public static Stone classify(Province p, double elevation, double relief) {
        return classify(p, elevation, relief, GeologySettings.DEFAULT);
    }
    public static Stone classify(Province p, double elevation, double relief, GeologySettings settings) {
        if (!Double.isFinite(elevation) || !Double.isFinite(relief) || relief < 0)
            throw new IllegalArgumentException("invalid terrain");
        double r = unit(p.identity() ^ 0x461aL);
        if (elevation < settings.oceanCeilingMetres()) return r < 0.75 ? Stone.GABBRO : Stone.LIMESTONE;
        if (elevation < settings.lowlandCeilingMetres() && relief < settings.gentleReliefMetres()) return r < 0.80 ? Stone.LIMESTONE : Stone.SLATE;
        if (relief > settings.ruggedReliefMetres() || elevation > settings.mountainFloorMetres()) return r < 0.65 ? Stone.QUARTZITE : Stone.SLATE;
        return r < 0.65 ? Stone.SLATE : r < 0.85 ? Stone.QUARTZITE : Stone.GABBRO;
    }
}
