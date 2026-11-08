package dev.wilyjeb.retainedclient;

import dev.wilyjeb.geology.probe.RetainedMapScreen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(TitleScreen.class)
public abstract class TitleOnly extends Screen {
    protected TitleOnly(Component title) { super(title); }
    @Inject(method="init", at=@At("HEAD"), cancellable=true)
    private void retained$title(CallbackInfo ci) {
        addRenderableWidget(Button.builder(Component.literal("Retained map (NO TD)"), b -> {
            System.out.println("RETAINED_CLIENT enter panel");
            minecraft.setScreen(new RetainedMapScreen(this));
        }).bounds(width/2-100,height/2-25,200,20).build());
        addRenderableWidget(Button.builder(Component.literal("Quit diagnostic"), b -> minecraft.stop())
            .bounds(width/2-100,height/2+5,200,20).build());
        System.out.println("RETAINED_CLIENT title: only map and quit; no world routes");
        ci.cancel();
    }
}
