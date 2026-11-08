package dev.wilyjeb.geology.probe;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** Probe-only map panel; never touches a world or TD. */
public final class RetainedMapScreen extends Screen {
    private final Screen parent;
    private final RetainedMap model=new RetainedMap();
    public RetainedMapScreen(Screen parent) {super(Component.literal("Retained regional comparison"));this.parent=parent;}
    @Override public void render(GuiGraphics g,int mouseX,int mouseY,float partialTick) {
        // Fixed readable logical canvas, fit to GUI viewport without changing map coordinates.
        double fit=Math.min(width/1200.0,height/900.0);
        g.pose().pushPose();g.pose().scale((float)fit,(float)fit,1);
        model.draw(new RetainedMap.Ink(){
            public void box(int x,int y,int w,int h,int c){g.fill(x,y,x+w,y+h,c);}
            public void text(String s,int x,int y,int c){g.drawString(font,s,x,y,c,false);}
            public void line(int x,int y,int xx,int yy,int c){
                int n=Math.max(Math.abs(xx-x),Math.abs(yy-y));
                for(int i=0;i<=n;i++){int px=x+(int)Math.round((xx-x)*(i/(double)Math.max(1,n)));int py=y+(int)Math.round((yy-y)*(i/(double)Math.max(1,n)));g.fill(px,py,px+1,py+1,c);}
            }
        },1200,900);
        g.pose().popPose();
    }
    @Override public boolean mouseClicked(double x,double y,int button) {
        if(button==0){double fit=Math.min(width/1200.0,height/900.0);model.click(x/fit,y/fit,1200,900);return true;}
        return super.mouseClicked(x,y,button);
    }
    @Override public void onClose(){minecraft.setScreen(parent);}
}
