package dev.wilyjeb.geology.probe.mixin;

import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(TitleScreen.class)
public abstract class RetainedMapTitleMixin extends Screen {
    protected RetainedMapTitleMixin(Component title){super(title);}
    @Inject(method="init",at=@At("RETURN"))
    private void retainedMap$button(CallbackInfo ci){
        if(Boolean.getBoolean("geology.probe.retainedMap")) addRenderableWidget(Button.builder(
            Component.literal("Retained map (debug)"),b->minecraft.setScreen(new dev.wilyjeb.geology.probe.RetainedMapScreen(this)))
            .bounds(5,5,160,20).build());
    }
}
