package dev.wilyjeb.retainedclient.mixin;
import dev.wilyjeb.retainedclient.Navigation;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.*;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(TitleScreen.class)
public abstract class TitleOnly extends Screen {
 protected TitleOnly(Component c){super(c);}
 @Inject(method="init",at=@At("HEAD"),cancellable=true)
 private void title(CallbackInfo ci){
  if(!Navigation.started)addRenderableWidget(Button.builder(Component.literal("NEW vanilla navigation (NO TD)"),b->Navigation.create(this)).bounds(width/2-120,height/2-35,240,20).build());
  addRenderableWidget(Button.builder(Component.literal("Retained inspection panel"),b->Navigation.panel(this)).bounds(width/2-120,height/2-10,240,20).build());
  addRenderableWidget(Button.builder(Component.literal("Quit diagnostic"),b->minecraft.stop()).bounds(width/2-120,height/2+15,240,20).build());
  System.out.println("RETAINED_NAV restricted title");ci.cancel();
 }
}
