package dev.wilyjeb.retainedclient;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;

@Mod(value="retained_client", dist=Dist.CLIENT)
public final class Diagnostic {
    public Diagnostic() {
        System.out.println("RETAINED_CLIENT display-only mod; no production or TD dependencies");
    }
}
