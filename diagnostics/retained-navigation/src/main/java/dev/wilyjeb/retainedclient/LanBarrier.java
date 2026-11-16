package dev.wilyjeb.retainedclient.mixin;
import net.minecraft.client.server.IntegratedServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(IntegratedServer.class)
public abstract class LanBarrier {
 @Inject(method="publishServer",at=@At("HEAD"),cancellable=true)
 private void noLan(CallbackInfoReturnable<Boolean> ci){System.out.println("RETAINED_NAV LAN rejected");ci.setReturnValue(false);}
}
