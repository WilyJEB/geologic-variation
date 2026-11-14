package dev.wilyjeb.retainedclient.mixin;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.*;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(DisconnectedScreen.class)
public abstract class DisconnectedOnly extends Screen {
 protected DisconnectedOnly(Component c){super(c);}
 @Inject(method="init",at=@At("HEAD"),cancellable=true)
 private void restrict(CallbackInfo ci){addRenderableWidget(Button.builder(Component.literal("Diagnostic title"),b->minecraft.setScreen(new TitleScreen())).bounds(width/2-100,height/2,200,20).build());addRenderableWidget(Button.builder(Component.literal("Quit diagnostic"),b->minecraft.stop()).bounds(width/2-100,height/2+25,200,20).build());ci.cancel();}
}
