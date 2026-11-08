package dev.wilyjeb.retainedclient.mixin;
import dev.wilyjeb.retainedclient.Navigation;
import net.minecraft.client.gui.*;
import net.minecraft.client.DeltaTracker;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(Gui.class)
public abstract class Hud {
 @Inject(method="render",at=@At("TAIL"))
 private void hud(GuiGraphics g,DeltaTracker dt,CallbackInfo ci){Navigation.draw(g);}
}
