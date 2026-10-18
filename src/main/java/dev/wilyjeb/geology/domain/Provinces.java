package dev.wilyjeb.geology.domain;

/** Pure immutable province partition. Version 1 is a worldgen contract. */
public final class Provinces {
    public enum Stone { LIMESTONE, SLATE, QUARTZITE, GABBRO }
    public record Province(long cellX, long cellZ, int anchorX, int anchorZ, long identity) {}
    private Provinces() {}
    public static long mix(long n) {
        n = (n ^ (n >>> 30)) * 0xbf58476d1ce4e5b9L;
        n = (n ^ (n >>> 27)) * 0x94d049bb133111ebL;
        return n ^ (n >>> 31);
    }
    private static double unit(long n) { return (mix(n) >>> 11) * 0x1.0p-53; }
    public static Province at(long seed, int scale, int x, int z) {
        if (scale < 1 || scale > 6) throw new IllegalArgumentException("scale must be 1..6");
        int spacing = 2048 * scale;
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
        if (!Double.isFinite(elevation) || !Double.isFinite(relief) || relief < 0)
            throw new IllegalArgumentException("invalid terrain");
        double r = unit(p.identity() ^ 0x461aL);
        if (elevation < -200) return r < 0.75 ? Stone.GABBRO : Stone.LIMESTONE;
        if (elevation < 600 && relief < 300) return r < 0.80 ? Stone.LIMESTONE : Stone.SLATE;
        if (relief > 600 || elevation > 1800) return r < 0.65 ? Stone.QUARTZITE : Stone.SLATE;
        return r < 0.65 ? Stone.SLATE : r < 0.85 ? Stone.QUARTZITE : Stone.GABBRO;
    }
}