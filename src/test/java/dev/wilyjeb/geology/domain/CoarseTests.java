package dev.wilyjeb.geology.domain;

public final class CoarseTests {
    private static void check(boolean b) { if (!b) throw new AssertionError("Coarse contract"); }
    public static void main(String[] args) {
        for (int scale : new int[]{1,6}) {
            int stride = 256 * scale;
            for (int cell = -20; cell <= 20; cell++) {
                check(CoarseEvidence.index(cell*stride,scale)==cell);
                check(CoarseEvidence.index(cell*stride-1,scale)==cell-1);
                check(CoarseEvidence.index(cell*stride+stride-1,scale)==cell);
            }
        }
        check(CoarseEvidence.decode(-6,2,0)==-9);
        check(CoarseEvidence.decode(6,2,1)==9);
        check(CoarseEvidence.decode(6,2,2)==3);
        for (float w : new float[]{0,-1,1e-9f,Float.NaN,Float.POSITIVE_INFINITY})
            check(Double.isNaN(CoarseEvidence.decode(1,w,0)));
        check(Double.isNaN(CoarseEvidence.decode(Float.NaN,1,0)));
        check(Double.isNaN(CoarseEvidence.decode(Float.MAX_VALUE,1e-7f,0)));
        var original = new GenerationContext(GenerationContext.GENERATOR,42,1,256,"td","models","CPU/os/arch");
        var experimental = new GenerationContext(CoarseEvidence.VERSION,42,1,256,"td","models","CPU/os/arch");
        try { original.requireCompatible(experimental); throw new AssertionError("Version crossed"); }
        catch (GenerationContext.Mismatch expected) { check(expected.fields().equals("generator")); }
        try { experimental.requireCompatible(experimental); throw new AssertionError("Prototype became a generator"); }
        catch (GenerationContext.Mismatch expected) { check(expected.fields().equals("generator")); }
        original.requireCompatible(original);
        System.out.println("Coarse coordinate, signal and generator boundary tests passed");
    }
}
