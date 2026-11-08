package dev.wilyjeb.retainedclient.mixin;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class WorldBarrier {
    @Inject(method="setLevel", at=@At("HEAD"))
    private void retained$noLevel(ClientLevel level, net.minecraft.client.gui.screens.ReceivingLevelScreen.Reason reason, CallbackInfo ci) {
        if(level!=null) throw new IllegalStateException("RETAINED_CLIENT world attachment prohibited");
    }
    @Inject(method="doWorldLoad", at=@At("HEAD"))
    private void retained$noServer(CallbackInfo ci) {
        throw new IllegalStateException("RETAINED_CLIENT integrated server prohibited");
    }
}
