package dev.wilyjeb.retainedclient.mixin;
import dev.wilyjeb.retainedclient.Navigation;
import net.minecraft.world.level.storage.LevelStorageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(LevelStorageSource.class)
public abstract class SaveBarrier {
 @Inject(method={"createAccess","validateAndCreateAccess"},at=@At("HEAD"))
 private void save(String name,CallbackInfoReturnable<LevelStorageSource.LevelStorageAccess> ci){Navigation.checkSave(((LevelStorageSource)(Object)this).getBaseDir(),name);}
}
