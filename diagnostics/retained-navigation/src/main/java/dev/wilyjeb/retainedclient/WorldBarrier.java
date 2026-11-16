package dev.wilyjeb.retainedclient.mixin;
import dev.wilyjeb.retainedclient.Navigation;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.server.WorldStem;
import net.minecraft.server.packs.repository.PackRepository;
import net.minecraft.world.level.storage.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(Minecraft.class)
public abstract class WorldBarrier {
 @Inject(method="doWorldLoad",at=@At("HEAD"))
 private void server(LevelStorageSource.LevelStorageAccess access,PackRepository packs,WorldStem stem,boolean fresh,CallbackInfo ci){
  if(!Navigation.creating||Navigation.started||!fresh||!access.getLevelId().equals("navigation-only")||!access.getLevelPath(LevelResource.ROOT).toAbsolutePath().normalize().equals(Navigation.root().resolve("saves/navigation-only")))throw new IllegalStateException("Navigation server rejected");
  Navigation.started=true;System.out.println("RETAINED_NAV guard fresh integrated server");
 }
 @Inject(method="setLevel",at=@At("HEAD"))
 private void level(ClientLevel level,net.minecraft.client.gui.screens.ReceivingLevelScreen.Reason reason,CallbackInfo ci){
  if(level!=null){if(!Navigation.started||!Minecraft.getInstance().hasSingleplayerServer())throw new IllegalStateException("Remote level rejected");System.out.println("RETAINED_NAV guard local attachment");}
 }
}
