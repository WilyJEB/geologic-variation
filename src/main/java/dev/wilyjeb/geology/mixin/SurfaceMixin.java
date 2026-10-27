package dev.wilyjeb.geology.mixin;
import com.github.xandergos.terraindiffusionmc.world.TerrainDiffusionBiomeSource;
import dev.wilyjeb.geology.GeologicVariation;
import dev.wilyjeb.geology.Geology;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.block.Blocks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(NoiseBasedChunkGenerator.class)
public abstract class SurfaceMixin {
    @Inject(method = "buildSurface(Lnet/minecraft/server/level/WorldGenRegion;Lnet/minecraft/world/level/StructureManager;Lnet/minecraft/world/level/levelgen/RandomState;Lnet/minecraft/world/level/chunk/ChunkAccess;)V", at = @At("RETURN"))
    private void geology$surface(WorldGenRegion region, StructureManager structures,
                                  RandomState random, ChunkAccess chunk, CallbackInfo ci) {
        var generator = (NoiseBasedChunkGenerator)(Object)this;
        if (!region.getLevel().dimension().equals(Level.OVERWORLD)
                || !(generator.getBiomeSource() instanceof TerrainDiffusionBiomeSource)) return;
        var pos = new BlockPos.MutableBlockPos();
        int sx = chunk.getPos().getMinBlockX(), sz = chunk.getPos().getMinBlockZ();
        // Resolve all potentially blocking queries before changing this chunk.
        var materials = new dev.wilyjeb.geology.domain.Provinces.Stone[256];
        for (int z = 0; z < 16; z++) for (int x = 0; x < 16; x++)
            materials[z * 16 + x] = Geology.regionAt(region.getLevel().getServer(), sx + x, sz + z).stone();
        dev.wilyjeb.geology.WorldGeologySettings.current(region.getLevel().getServer());
        for (int z = sz; z < sz+16; z++) for (int x = sx; x < sx+16; x++) {
            var material = materials[(z - sz) * 16 + x - sx];
            var host = material.layer() == dev.wilyjeb.geology.domain.Provinces.Layer.DEEP
                    ? Blocks.DEEPSLATE : Blocks.STONE;
            var stone = GeologicVariation.STONES.get(material).get().defaultBlockState();
            for (int y = chunk.getMinBuildHeight(); y < chunk.getMaxBuildHeight(); y++) {
                pos.set(x, y, z);
                if (chunk.getBlockState(pos).is(host)) chunk.setBlockState(pos, stone, false);
            }
        }
    }
}
