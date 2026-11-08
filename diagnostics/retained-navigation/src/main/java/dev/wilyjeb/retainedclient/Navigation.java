package dev.wilyjeb.retainedclient;

import java.nio.file.*;
import dev.wilyjeb.geology.probe.RetainedMap;
import dev.wilyjeb.geology.probe.RetainedMapScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import org.lwjgl.glfw.GLFW;

/** One immutable fixture; no terrain reads, generation hooks or production state. */
public final class Navigation {
    public static boolean creating, started;
    public static boolean overlay=true;
    private static long logged;
    private static int route;
    private static final RetainedMap map=new RetainedMap();
    private static final int[][] ROUTE={{2944,13824},{2688,10880},{5760,10880},
        {2720,10912},{5760,13952},{5761,13953},{17664,82944}};

    public static Path root() {
        Path expected=Path.of(System.getProperty("retained.navigation.root", "INVALID")).toAbsolutePath().normalize();
        Path actual=Minecraft.getInstance().gameDirectory.toPath().toAbsolutePath().normalize();
        if(!expected.equals(actual) || !expected.getParent().getFileName().toString().equals("td-navigation-2")
            || !expected.getFileName().toString().matches("attempt-0[12]")) throw new IllegalStateException("Navigation root rejected");
        try {for(Path q=expected;q!=null;q=q.getParent()) if(Files.isSymbolicLink(q) || (Files.exists(q) && !q.toRealPath().equals(q))) throw new IllegalStateException("Redirected root");}
        catch(java.io.IOException e){throw new IllegalStateException(e);}
        return expected;
    }
    public static void checkSave(Path base,String name) {
        Path allowed=root().resolve("saves");
        if(!creating || started || !name.equals("navigation-only") || !base.toAbsolutePath().normalize().equals(allowed)
            || Files.exists(allowed.resolve(name)) || Files.isSymbolicLink(allowed)) throw new IllegalStateException("Navigation save rejected");
        System.out.println("RETAINED_NAV guard fresh save "+allowed.resolve(name));
    }
    public static void create(Screen parent) {
        if(creating || started || Files.exists(root().resolve("saves/navigation-only"))) throw new IllegalStateException("Navigation reuse rejected");
        creating=true;
        for(String rejected:new String[]{"../continuing","other-world"}) {
            try {checkSave(root().resolve("saves"),rejected);throw new AssertionError("Bad save accepted");}
            catch(IllegalStateException expected){System.out.println("RETAINED_NAV guard rejected "+rejected);}
        }
        map.selected=-1;
        try {
            var mc=Minecraft.getInstance();
            var rules=new GameRules();
            rules.getRule(GameRules.RULE_SPAWN_CHUNK_RADIUS).set(0,null);
            rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
            mc.createWorldOpenFlows().createFreshLevel("navigation-only",
                new LevelSettings("UNRELATED VANILLA NAVIGATION",GameType.CREATIVE,false,Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),
                new WorldOptions(8675309L,false,false),
                registry -> registry.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(WorldPresets.FLAT).value().createWorldDimensions(),parent);
        } finally {creating=false;}
    }
    public static void panel() { panel(null); }
    public static void panel(Screen parent) {
        System.out.println("RETAINED_NAV panel");
        Minecraft.getInstance().setScreen(new RetainedMapScreen(parent));
    }
    // Event-driven controls retain short taps; the executed polling revision is
    // separately retained in the evidence. This correction is compile-only.
    public static boolean key(int key,int action) {
        var mc=Minecraft.getInstance();
        if(action!=GLFW.GLFW_PRESS || mc.player==null || mc.screen!=null)return false;
        switch(key) {
            case GLFW.GLFW_KEY_H -> {overlay=!overlay;System.out.println("RETAINED_NAV overlay "+overlay);}
            case GLFW.GLFW_KEY_P -> panel();
            case GLFW.GLFW_KEY_V -> map.mode=1-map.mode;
            case GLFW.GLFW_KEY_B -> map.scale=7-map.scale;
            case GLFW.GLFW_KEY_R -> {int[] pos=ROUTE[route];map.scale=route==6?6:1;mc.player.connection.sendCommand("tp @s "+pos[0]+" 100 "+pos[1]+" 0 0");System.out.println("RETAINED_NAV route "+route);route=(route+1)%ROUTE.length;}
            default -> {return false;}
        }
        return true;
    }
    public static void draw(GuiGraphics g) {
        var mc=Minecraft.getInstance(); if(mc.player==null || mc.level==null)return;
        double x=mc.player.getX(),z=mc.player.getZ(),nx=x/map.scale,nz=z/map.scale;
        long bx=(long)Math.floor(x),bz=(long)Math.floor(z);
        boolean inside=nx>=2688&&nx<5761&&nz>=10880&&nz<13953;
        boolean site=map.sites.stream().anyMatch(s->nx==s.x()&&nz==s.z());
        if(System.currentTimeMillis()-logged>=1000){logged=System.currentTimeMillis();System.out.printf(java.util.Locale.ROOT,"RETAINED_NAV position %.6f %.6f scale %d block %d %d chunk %d %d support %s%n",x,z,map.scale,bx,bz,RetainedMap.chunk(bx),RetainedMap.chunk(bz),site?"site":inside?"gap":"exterior");}
        if(!overlay || mc.screen!=null)return;
        float fit=Math.min(mc.getWindow().getGuiScaledWidth()/1700f,mc.getWindow().getGuiScaledHeight()/1800f);
        g.pose().pushPose();g.pose().scale(fit,fit,1);
        map.draw(new RetainedMap.Ink(){
            public void box(int a,int b,int w,int h,int c){g.fill(a,b,a+w,b+h,c);}
            public void text(String s,int a,int b,int c){g.drawString(mc.font,s,a,b,c,false);}
            public void line(int a,int b,int c,int d,int color){int n=Math.max(Math.abs(c-a),Math.abs(d-b));for(int i=0;i<=n;i++){int xx=a+(int)Math.round((c-a)*i/(double)Math.max(1,n)),zz=b+(int)Math.round((d-b)*i/(double)Math.max(1,n));g.fill(xx,zz,xx+1,zz+1,color);}}
        },1200,900);
        int size=map.mapSize(1200,900);
        int mx=20+(int)Math.round((Math.max(2688,Math.min(5761,nx))-2688)/3073*size);
        int mz=62+(int)Math.round((Math.max(10880,Math.min(13953,nz))-10880)/3073*size);
        g.fill(mx-10,mz-2,mx+11,mz+3,0xffff00ff);g.fill(mx-2,mz-10,mx+3,mz+11,0xffff00ff);
        g.pose().popPose();
        int y=(int)(900*fit)+4;
        String[] lines={"UNRELATED VANILLA FLAT WORLD - navigation only; NO TD",
            String.format(java.util.Locale.ROOT,"Player X %.3f Z %.3f | blocks %d,%d | chunks %d,%d",x,z,bx,bz,RetainedMap.chunk(bx),RetainedMap.chunk(bz)),
            "Scale "+map.scale+" native "+String.format(java.util.Locale.ROOT,"%.3f,%.3f",nx,nz)+" | "+(site?"exact retained site":inside?"UNSUPPORTED GAP":"EXTERIOR UNKNOWN"),
            "H HUD | P full inspection | V PR58/59 | B scale1/6 | R next fixed route",
            "Magenta = actual player; edge-clamped outside. TD metres NEVER Minecraft Y."};
        for(String line:lines){g.fill(0,y-1,mc.getWindow().getGuiScaledWidth(),y+10,0xd014232c);g.drawString(mc.font,line,3,y,0xffffffff,false);y+=11;}
    }
}
