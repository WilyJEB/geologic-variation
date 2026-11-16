package dev.wilyjeb.retainedclient.mixin;
import dev.wilyjeb.retainedclient.Navigation;
import net.minecraft.client.KeyboardHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(KeyboardHandler.class)
public abstract class Keys {
 @Inject(method="keyPress",at=@At("HEAD"),cancellable=true)
 private void keys(long window,int key,int scan,int action,int modifiers,CallbackInfo ci){if(Navigation.key(key,action))ci.cancel();}
}
