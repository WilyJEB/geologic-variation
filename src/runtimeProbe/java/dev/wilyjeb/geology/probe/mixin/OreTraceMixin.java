package dev.wilyjeb.geology.probe.mixin;

import dev.wilyjeb.geology.probe.CoalTrace;
import java.util.function.Function;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.OreFeature;
import net.minecraft.world.level.levelgen.feature.configurations.OreConfiguration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(OreFeature.class)
public abstract class OreTraceMixin {
    @Inject(method="place",at=@At("HEAD"))
    private void trace$begin(FeaturePlaceContext<OreConfiguration> context,CallbackInfoReturnable<Boolean> ci) {
        CoalTrace.begin(context);
    }
    @Inject(method="place",at=@At("RETURN"))
    private void trace$end(FeaturePlaceContext<OreConfiguration> context,CallbackInfoReturnable<Boolean> ci) {
        CoalTrace.end(context,ci.getReturnValue());
    }
    @Inject(method="canPlaceOre",at=@At("HEAD"))
    private static void trace$before(BlockState state,Function<BlockPos,BlockState> getter,RandomSource random,
        OreConfiguration config,OreConfiguration.TargetBlockState target,BlockPos.MutableBlockPos pos,CallbackInfoReturnable<Boolean> ci) {
        CoalTrace.beforeCheck(state,random,target,pos);
    }
    @Inject(method="canPlaceOre",at=@At("RETURN"))
    private static void trace$after(BlockState state,Function<BlockPos,BlockState> getter,RandomSource random,
        OreConfiguration config,OreConfiguration.TargetBlockState target,BlockPos.MutableBlockPos pos,CallbackInfoReturnable<Boolean> ci) {
        CoalTrace.afterCheck(random,ci.getReturnValue());
    }
    @Redirect(method="doPlace",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/chunk/LevelChunkSection;setBlockState(IIILnet/minecraft/world/level/block/state/BlockState;Z)Lnet/minecraft/world/level/block/state/BlockState;"))
    private BlockState trace$write(LevelChunkSection section,int x,int y,int z,BlockState target,boolean locked) {
        var previous=section.setBlockState(x,y,z,target,locked);
        CoalTrace.wrote(x,y,z,previous,target);
        return previous;
    }
}
