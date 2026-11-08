package dev.wilyjeb.geology.probe;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Fixed retained map model and drawing commands; no Minecraft/provider/world APIs. */
public final class RetainedMap {
    public record Site(int x, int z, double height, String baseline, String story) {}
    public record History(int mode, String id, String token, String seed, String measured, String authored) {}
    public record Line(int mode, double x1, double z1, double x2, double z2) {}
    public interface Ink {
        void box(int x, int y, int w, int h, int color);
        void text(String s, int x, int y, int color);
        void line(int x, int y, int xx, int yy, int color);
    }
    public final List<Site> sites;
    public final List<History> histories;
    public final List<Line> lines;
    public int mode = 1, scale = 1, selected = 0;
    private static final int WHITE=0xffeeeeee, MUTED=0xffb9c6cd;
    public RetainedMap() {
        var ps=new ArrayList<Site>(); var hs=new ArrayList<History>(); var ls=new ArrayList<Line>();
        try (var input=RetainedMap.class.getResourceAsStream("/retained-map.tsv")) {
            if(input==null) throw new IOException("Missing retained resource");
            byte[] bytes=input.readNBytes(2*1024*1024+1);
            if(bytes.length>2*1024*1024) throw new IOException("Resource cap");
            for(String row:new String(bytes,StandardCharsets.UTF_8).split("\n")) {
                String[] v=row.split("\t");
                switch(v[0]) {
                    case "P" -> ps.add(new Site(Integer.parseInt(v[1]),Integer.parseInt(v[2]),Double.parseDouble(v[3]),v[4],v[5]));
                    case "H" -> hs.add(new History(Integer.parseInt(v[1]),v[2],v[3],v[4],v[5],v[6]));
                    case "L" -> ls.add(new Line(Integer.parseInt(v[1]),Double.parseDouble(v[2]),Double.parseDouble(v[3]),Double.parseDouble(v[4]),Double.parseDouble(v[5])));
                    default -> { if(!v[0].startsWith("#")) throw new IOException("Unknown record"); }
                }
            }
            if(ps.size()!=2401 || hs.size()!=7 || ls.size()>512) throw new IOException("Record caps");
            sites=List.copyOf(ps); histories=List.copyOf(hs); lines=List.copyOf(ls);
        } catch(IOException | RuntimeException e) { throw new IllegalStateException("Retained map rejected",e); }
    }
    public static long block(double nativeCoordinate,int scale) {
        if(scale!=1 && scale!=6 || !Double.isFinite(nativeCoordinate) || Math.abs(nativeCoordinate)>30_000_000.0/scale)
            throw new IllegalArgumentException("Coordinate/scale cap");
        return (long)Math.floor(nativeCoordinate*scale);
    }
    public static long chunk(long block) { return Math.floorDiv(block,16); }
    public static int local(long block) { return (int)Math.floorMod(block,16); }
    public String id(Site s) { return mode==0?s.baseline:s.story; }
    public int mapSize(int width,int height) { return Math.max(48,Math.min(height-182,width-345)); }
    private static int px(double x,int size) { return 20+(int)Math.round((x-2688)/3073*size); }
    private static int pz(double z,int size) { return 62+(int)Math.round((z-10880)/3073*size); }
    public void click(double x,double y,int width,int height) {
        if(y>=24 && y<49) {
            if(x<220) mode=1-mode; else if(x<420) scale=7-scale;
            return;
        }
        int size=mapSize(width,height); double best=36; selected=-1;
        for(int i=0;i<sites.size();i++) {
            Site s=sites.get(i); double d=Math.pow(x-px(s.x,size),2)+Math.pow(y-pz(s.z,size),2);
            if(d<best) {best=d;selected=i;}
        }
    }
    public void draw(Ink g,int width,int height) {
        g.box(0,0,width,height,0xff14232c);
        g.text("RETAINED PR58 / PR59 - diagnostic; unrelated to any loaded world",20,8,WHITE);
        g.box(20,24,190,24,0xff365363); g.box(220,24,190,24,0xff365363);
        g.text(mode==0?"PR58 boundary [toggle]":"PR59 history [toggle]",25,31,WHITE);
        g.text("Display scale "+scale+" [toggle]",225,31,WHITE);
        int size=mapSize(width,height), right=size+40;
        g.box(19,61,size+2,size+2,0xff9aaeb9);g.box(20,62,size,size,0xff26333a);
        // Clip each conceptual segment to the original half-open query rectangle.
        for(Line l:lines) if(l.mode==mode) {
            double[] v=clip(l);
            if(v!=null) g.line(px(v[0],size),pz(v[1],size),px(v[2],size),pz(v[3],size),0xffe5bb7a);
        }
        for(Site s:sites) {
            float t=(float)((s.height+4861.288)/7822.2753);
            int rgb=java.awt.Color.HSBtoRGB(.61f-.53f*t,.65f,.94f);
            g.box(px(s.x,size)-1,pz(s.z,size)-1,3,3,rgb);
        }
        for(History h:histories) if(h.mode==mode) {
            double sx=0,sz=0;int count=0;
            for(Site s:sites) if(id(s).equals(h.id)) {sx+=s.x;sz+=s.z;count++;}
            if(count>0) {int x=px(sx/count,size), y=pz(sz/count,size);g.box(x-3,y-3,62,15,0xff14232c);g.text("ID "+h.id,x,y,WHITE);}
        }
        String[] notes={"Actual sites: 49 x 49 = 2,401", "Blue low / orange high (TD metres)",
            "Gold = conceptual contacts", "Outer box = original query footprint", "Gaps / exterior heights UNKNOWN",
            "9,440,928 query values unavailable", "Error unknown; geology abstains", "Click an actual sample for its story", "",
            "Native X 2688 .. 5761 exclusive", "Native Z 10880 .. 13953 exclusive",
            "X blocks "+2688*scale+" .. "+5761*scale+" exclusive", "Z blocks "+10880*scale+" .. "+13953*scale+" exclusive",
            "Footprint side "+3073*scale+" blocks", "Sample spacing "+64*scale+" blocks ("+4*scale+" chunks)",
            "Nominal band width "+2048*scale+" blocks", "= "+128*scale+" chunks along X", "Native +X right, +Z down; origin fixed"};
        for(int i=0;i<notes.length;i++) g.text(notes[i],right,65+13*i,MUTED);
        int y=65+13*notes.length;
        if(selected>=0) {
            Site s=sites.get(selected);long bx=block(s.x,scale), bz=block(s.z,scale);
            int x=px(s.x,size),z=pz(s.z,size);g.box(x-4,z-4,9,1,WHITE);g.box(x-4,z+4,9,1,WHITE);g.box(x-4,z-4,1,9,WHITE);g.box(x+4,z-4,1,9,WHITE);
            var h=histories.stream().filter(v->v.mode==mode && v.id.equals(id(s))).findFirst().orElseThrow();
            String[] card={"SELECTED ID "+h.id+" / native "+s.x+", "+s.z,
                "Blocks "+bx+", "+bz, "Chunks "+chunk(bx)+", "+chunk(bz)+"; local "+local(bx)+", "+local(bz),
                String.format(java.util.Locale.ROOT,"Measured height %.3f m; not Minecraft Y",s.height),
                "SEED: "+h.seed, "MEASURED:",h.measured,"AUTHORED SURFACE:",h.authored,
                "DEEP: same inherited ID / token",h.token.substring(0,32),h.token.substring(32),
                "Surface and deep share the full token", "UNKNOWN: depth, rock, age, true history"};
            for(String t:card) {g.text(t,right,y,WHITE);y+=13;}
        } else g.text("No retained sample selected; support unknown",right,y,WHITE);
        int bottom=height-104;
        g.text("3073 native pixels = "+3073*scale+" Minecraft blocks; 16 blocks = one chunk",20,bottom,WHITE);
        g.line(20,bottom+22,20+(int)Math.round(512.0/3073*size),bottom+22,WHITE);
        g.text("512 native = "+512*scale+" blocks / "+32*scale+" chunks",20,bottom+30,WHITE);
        g.text("PR59: gx=-0.541055, gz=0.545010; authored tilt a=-0.5 (clamped).",20,bottom+49,MUTED);
        g.text("PR59 did NOT establish better landscape-related contacts. No terrain between points is observed.",20,bottom+64,MUTED);
        g.text("Surface/deep card is conceptual, not a 3D interface. No production selection or saved settings.",20,bottom+79,MUTED);
    }
    // Liang-Barsky clipping of contact geometry only, never height interpolation.
    static double[] clip(Line l) {
        double dx=l.x2-l.x1,dz=l.z2-l.z1,lo=0,hi=1;
        double[] p={-dx,dx,-dz,dz},q={l.x1-2688,5761-l.x1,l.z1-10880,13953-l.z1};
        for(int i=0;i<4;i++) {
            if(p[i]==0) {if(q[i]<0)return null;continue;}
            double t=q[i]/p[i];if(p[i]<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);
        }
        return lo>hi?null:new double[]{l.x1+lo*dx,l.z1+lo*dz,l.x1+hi*dx,l.z1+hi*dz};
    }
    /** Isolated diagnostic route: JDK only, no MC or TD classes loaded. */
    public static void main(String[] args) throws Exception {
        RetainedMap model=new RetainedMap();
        if(args.length>0 && args[0].equals("--check")) {
            for(int scale:new int[]{1,6}) for(int edge=-32;edge<=32;edge+=16) for(int b=edge-1;b<=edge+1;b++) {
                if(block(b/(double)scale,scale)!=b || chunk(b)*16+local(b)!=b || local(b)<0 || local(b)>15)
                    throw new AssertionError("Signed conversion/chunk edge");
            }
            for(int scale:new int[]{1,6}) for(Site s:model.sites)
                if(block(s.x,scale)!=s.x*(long)scale || block(s.z,scale)!=s.z*(long)scale) throw new AssertionError("Site conversion");
            model.click(30,32,1200,900);if(model.mode!=0)throw new AssertionError("Mode toggle");
            model.click(230,32,1200,900);if(model.scale!=6)throw new AssertionError("Scale toggle");
            model.click(20,62,1200,900);if(model.selected!=0)throw new AssertionError("Sample click");
            model.click(27,69,1200,900);if(model.selected!=-1)throw new AssertionError("Gap must remain unknown");
            for(Line l:model.lines) {double[] v=clip(l);if(v!=null && (v[0]<2688 || v[2]>5761 || v[1]<10880 || v[3]>13953)) throw new AssertionError("Clip bound");}
            System.out.println("PASS Java coordinates, signed chunks, retained sites, toggles, hit testing, contact bounds");
            return;
        }
        if(args.length>0 && args[0].equals("--render")) {
            for(int mode=0;mode<2;mode++) for(int scale:new int[]{1,6}) {
                model.mode=mode;model.scale=scale;
                var image=new java.awt.image.BufferedImage(1200,900,java.awt.image.BufferedImage.TYPE_INT_RGB);
                var g=image.createGraphics();drawDesktop(model,g,1200,900);g.dispose();
                javax.imageio.ImageIO.write(image,"png",new File(args[1]+"-"+mode+"-"+scale+".png"));
            }
            return;
        }
        javax.swing.SwingUtilities.invokeLater(()->{
            var frame=new javax.swing.JFrame("Geologic Variation - retained diagnostic only");
            var panel=new javax.swing.JPanel() {
                protected void paintComponent(java.awt.Graphics g) {super.paintComponent(g);drawDesktop(model,(java.awt.Graphics2D)g,getWidth(),getHeight());}
            };
            panel.setPreferredSize(new java.awt.Dimension(1200,900));
            panel.addMouseListener(new java.awt.event.MouseAdapter(){public void mouseClicked(java.awt.event.MouseEvent e){model.click(e.getX(),e.getY(),panel.getWidth(),panel.getHeight());panel.repaint();}});
            frame.setContentPane(panel);frame.pack();frame.setMinimumSize(new java.awt.Dimension(1000,850));
            frame.setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);frame.setVisible(true);
        });
    }
    static void drawDesktop(RetainedMap model,java.awt.Graphics2D g,int w,int h) {
        g.setFont(new java.awt.Font("Monospaced",java.awt.Font.PLAIN,12));
        model.draw(new Ink(){
            public void box(int x,int y,int ww,int hh,int c){g.setColor(new java.awt.Color(c,true));g.fillRect(x,y,ww,hh);}
            public void text(String s,int x,int y,int c){g.setColor(new java.awt.Color(c,true));g.drawString(s,x,y+10);}
            public void line(int x,int y,int xx,int yy,int c){g.setColor(new java.awt.Color(c,true));g.drawLine(x,y,xx,yy);}
        },w,h);
    }
}
