package dev.wilyjeb.geology.domain;
import java.util.*;
public final class GeologyTests {
    private static void check(boolean value) { if (!value) throw new AssertionError(); }
    public static void main(String[] args) {
        Set<Provinces.Stone> stones = EnumSet.noneOf(Provinces.Stone.class);
        for (int scale = 1; scale <= 6; scale++) for (int x = -20000; x < 20000; x += 137) {
            var p = Provinces.at(1234, scale, x, -x);
            check(p.equals(Provinces.at(1234, scale, x, -x)));
            check(p.equals(Provinces.at(1234, scale, p.anchorX(), p.anchorZ())));
            check(!p.equals(Provinces.at(1235, scale, x, -x)));
            for (double h : new double[]{-800, 100, 1000, 3000})
                stones.add(Provinces.classify(p,h, h == 3000 ? 900 : 100));
        }
        check(stones.size() == 4);
        Map<String, Provinces.Province> expected = new HashMap<>();
        for (int z=-17; z<=17; z++) for(int x=-17; x<=17; x++)
            expected.put(x+":"+z,Provinces.at(42,1,x,z));
        for(int x=17;x>=-17;x--) for(int z=17;z>=-17;z--)
            check(expected.get(x+":"+z).equals(Provinces.at(42,1,x,z)));
        try { Provinces.at(0,0,0,0); throw new AssertionError(); } catch(IllegalArgumentException good) {}
        try { Provinces.classify(Provinces.at(0,1,0,0),Double.NaN,0); throw new AssertionError(); }
        catch(IllegalArgumentException good) {}
        System.out.println("Province determinism, seed separation, anchor stability, traversal, negative coordinates, four stones and validation passed.");
    }
}