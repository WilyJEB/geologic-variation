package dev.wilyjeb.geology.probe;

import com.google.gson.GsonBuilder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.WorldgenRandom;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.OreConfiguration;

/** Opt-in, bounded observation of natural coal eligibility and ore writes. Never draws random values. */
public final class CoalTrace {
    private static final int LIMIT = 500000;
    private static final Set<ChunkPos> WATCHED = new HashSet<>();
    private static final ArrayList<Map<String,Object>> EVENTS = new ArrayList<>();
    private static final Map<String,Integer> INVOCATIONS = new HashMap<>();
    private static final ThreadLocal<Placement> CURRENT = new ThreadLocal<>();
    private static final ThreadLocal<Map<String,Object>> FEATURE_SEED = new ThreadLocal<>();
    private static volatile boolean enabled;
    private static boolean overflow;
    private static int unmatchedWrites;
    private static final class Placement {
        final String key;
        final boolean nearby;
        final boolean coal;
        Candidate candidate;
        Placement(String key,boolean nearby,boolean coal) { this.key=key;this.nearby=nearby;this.coal=coal; }
    }
    private record Candidate(BlockPos pos,String previous,String target,int before) {}
    private CoalTrace() {}
    public static synchronized Map<String,Object> reset() {
        enabled=false;WATCHED.clear();EVENTS.clear();INVOCATIONS.clear();overflow=false;unmatchedWrites=0;
        return summary();
    }
    public static synchronized Map<String,Object> watch(int x,int z) {
        if(WATCHED.size()>=16) throw new IllegalArgumentException("At most 16 watched chunks");
        WATCHED.add(new ChunkPos(x,z));enabled=true;return summary();
    }
    public static synchronized Map<String,Object> summary() {
        return Map.of("kind","coal-trace","watched",WATCHED.stream().map(p -> java.util.List.of(p.x,p.z)).toList(),
            "events",EVENTS.size(),"overflow",overflow,"unmatched_writes",unmatchedWrites,"source_halo",2,"record_limit",LIMIT);
    }
    public static synchronized void flush() {
        if(!enabled) return;
        try {
            var result=new LinkedHashMap<String,Object>(summary());result.put("records",EVENTS);
            Files.writeString(Path.of("coal-write-trace.json"),new GsonBuilder().setPrettyPrinting().create().toJson(result));
        } catch(java.io.IOException e) { throw new RuntimeException("Cannot export coal trace",e); }
    }
    private static int count(RandomSource random) { return random instanceof WorldgenRandom w ? w.getCount() : -1; }
    private static String id(BlockState state) { return BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString(); }
    private static synchronized void event(Map<String,Object> event) {
        if(EVENTS.size()>=LIMIT) { overflow=true;return; }
        var copy=new LinkedHashMap<String,Object>();copy.put("sequence",EVENTS.size());copy.putAll(event);EVENTS.add(copy);
    }
    private static synchronized boolean watched(BlockPos pos) { return WATCHED.contains(new ChunkPos(pos)); }
    public static void featureSeed(long seed,int index,int step) {
        if(enabled) FEATURE_SEED.set(Map.of("decoration_seed",seed,"feature_index",index,"step",step));
    }
    public static void begin(FeaturePlaceContext<OreConfiguration> context) {
        if(!enabled || !(context.level() instanceof WorldGenRegion region)) return;
        boolean coal=context.config().targetStates.stream().anyMatch(t -> t.state.is(Blocks.COAL_ORE) || t.state.is(Blocks.DEEPSLATE_COAL_ORE));
        // Also observe writes that remove coal-host eligibility, such as dirt/gravel/other ores.
        // Host-to-host granite/diorite/andesite writes cannot cause this early predicate failure.
        if(!coal && context.config().targetStates.stream().allMatch(t -> t.state.is(BlockTags.STONE_ORE_REPLACEABLES)
            || t.state.is(BlockTags.DEEPSLATE_ORE_REPLACEABLES))) return;
        var source=region.getCenter();var config=context.config();var origin=context.origin();
        var seed=FEATURE_SEED.get();
        String group=source.x+","+source.z+"/"+config.size+"/"+config.discardChanceOnAirExposure
            +"/"+(seed==null ? "unknown" : seed.get("feature_index")+":"+seed.get("step"));
        String key;boolean nearby;
        synchronized(CoalTrace.class) {
            int index=INVOCATIONS.merge(group,1,Integer::sum)-1;key=group+"/"+index;
            nearby=WATCHED.stream().anyMatch(p -> Math.abs(p.x-source.x)<=2 && Math.abs(p.z-source.z)<=2);
        }
        CURRENT.set(new Placement(key,nearby,coal));
        if(nearby) event(Map.of("event","begin","placement",key,"source",java.util.List.of(source.x,source.z),
            "origin",java.util.List.of(origin.getX(),origin.getY(),origin.getZ()),"random_count",count(context.random()),
            "size",config.size,"discard",config.discardChanceOnAirExposure,"feature_seed",seed==null ? Map.of() : seed,
            "targets",config.targetStates.stream().map(t -> id(t.state)).toList(),"coal",coal));
    }
    public static void end(FeaturePlaceContext<OreConfiguration> context,boolean placed) {
        var p=CURRENT.get();
        if(p!=null) {
            if(p.nearby) event(Map.of("event","end","placement",p.key,"placed",placed,"random_count",count(context.random())));
            CURRENT.remove();
        }
    }
    public static void beforeCheck(BlockState state,RandomSource random,OreConfiguration.TargetBlockState target,BlockPos pos) {
        var p=CURRENT.get();
        if(p!=null) p.candidate=new Candidate(pos.immutable(),id(state),id(target.state),count(random));
    }
    public static void afterCheck(RandomSource random,boolean accepted) {
        var p=CURRENT.get();
        if(p==null || !p.coal || p.candidate==null || (!p.nearby && !watched(p.candidate.pos))) return;
        var c=p.candidate;
        event(Map.of("event","check","placement",p.key,"position",java.util.List.of(c.pos.getX(),c.pos.getY(),c.pos.getZ()),
            "previous",c.previous,"target",c.target,"accepted",accepted,"random_before",c.before,"random_after",count(random)));
    }
    public static void wrote(int x,int y,int z,BlockState previous,BlockState target) {
        var p=CURRENT.get();
        if(p==null) return;
        var c=p.candidate;
        if(c==null || (c.pos.getX()&15)!=x || (c.pos.getY()&15)!=y || (c.pos.getZ()&15)!=z || !c.target.equals(id(target))) {
            synchronized(CoalTrace.class) { unmatchedWrites++; }return;
        }
        if(p.nearby || watched(c.pos)) event(Map.of("event","write","placement",p.key,
            "position",java.util.List.of(c.pos.getX(),c.pos.getY(),c.pos.getZ()),"previous",id(previous),"target",id(target)));
    }
}
