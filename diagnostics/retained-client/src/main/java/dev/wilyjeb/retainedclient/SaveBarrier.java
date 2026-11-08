package dev.wilyjeb.retainedclient.mixin;

import net.minecraft.world.level.storage.LevelStorageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(LevelStorageSource.class)
public abstract class SaveBarrier {
    @Inject(method={"createAccess", "validateAndCreateAccess"}, at=@At("HEAD"))
    private void retained$noSave(String name, CallbackInfoReturnable<LevelStorageSource.LevelStorageAccess> ci) {
        throw new IllegalStateException("RETAINED_CLIENT world/save access prohibited");
    }
}
