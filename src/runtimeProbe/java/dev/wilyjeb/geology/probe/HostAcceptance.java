package dev.wilyjeb.geology.probe;

import com.mojang.authlib.GameProfile;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.CarvingMask;
import net.minecraft.world.level.levelgen.Aquifer;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.carver.CarvingContext;
import net.minecraft.world.level.levelgen.carver.CaveCarverConfiguration;
import net.minecraft.world.level.levelgen.carver.CaveWorldCarver;
import net.minecraft.world.level.levelgen.feature.OreFeature;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import net.minecraft.world.level.levelgen.feature.configurations.OreConfiguration;
import net.minecraft.world.level.levelgen.structure.templatesystem.BlockMatchTest;
import net.minecraft.world.level.levelgen.structure.templatesystem.TagMatchTest;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import org.apache.commons.lang3.mutable.MutableBoolean;

/** Destructive, test-only fixture. Run only in a disposable frozen acceptance world. */
final class HostAcceptance {
    private static void require(boolean value, String message) {
        if (!value) throw new IllegalStateException(message);
    }
    static Map<String,Object> oreOrder(ServerLevel level) {
        var pos = new BlockPos(-504,220,-1032);
        var target = OreConfiguration.target(new TagMatchTest(BlockTags.STONE_ORE_REPLACEABLES),Blocks.COAL_ORE.defaultBlockState());
        var config = new OreConfiguration(List.of(target),17,0.5F);
        var forward = overlap(level,pos,Blocks.STONE.defaultBlockState(),config,false);
        var reverse = overlap(level,pos,Blocks.STONE.defaultBlockState(),config,true);
        var difference = new java.util.HashSet<>(forward);
        difference.removeAll(reverse);
        var other = new java.util.HashSet<>(reverse);
        other.removeAll(forward);
        require(!difference.isEmpty() || !other.isEmpty(),"Fixture did not reproduce order-dependent vanilla ore positions");
        var hosts = new ArrayList<Map<String,Object>>();
        for(String name:List.of("limestone","slate","quartzite","gabbro")) {
            var state = BuiltInRegistries.BLOCK.get(ResourceLocation.parse("geologic_variation:"+name)).defaultBlockState();
            require(overlap(level,pos,state,config,false).equals(forward),"Forward regional feature sequence differs from vanilla");
            require(overlap(level,pos,state,config,true).equals(reverse),"Reverse regional feature sequence differs from vanilla");
            hosts.add(Map.of("host",name,"forward_matches_stone",true,"reverse_matches_stone",true));
        }
        return Map.of("kind","ore-order","feature","minecraft:ore","size",17,"discard_chance_on_air_exposure",0.5,
            "owner_seeds",List.of(10,11),"attempts_per_owner",8,"forward_coal",forward.size(),"reverse_coal",reverse.size(),
            "changed_positions",difference.size()+other.size(),"hosts",hosts);
    }
    private static List<String> overlap(ServerLevel level,BlockPos pos,BlockState host,OreConfiguration config,boolean reverse) {
        for(var p:BlockPos.betweenClosed(pos.offset(-7,-7,-7),pos.offset(7,7,7))) level.setBlock(p,host,2);
        for(int index=0;index<2;index++) {
            int owner = reverse ? 1-index : index;
            var random = RandomSource.create(10+owner);
            for(int attempt=0;attempt<8;attempt++) {
                var origin = pos.offset(random.nextInt(5)-2,random.nextInt(5)-2,random.nextInt(5)-2);
                new ConfiguredFeature<>(Feature.ORE,config).place(level,level.getChunkSource().getGenerator(),random,origin);
            }
        }
        var result = new ArrayList<String>();
        for(var p:BlockPos.betweenClosed(pos.offset(-7,-7,-7),pos.offset(7,7,7)))
            if(level.getBlockState(p).is(Blocks.COAL_ORE)) result.add((p.getX()-pos.getX())+","+(p.getY()-pos.getY())+","+(p.getZ()-pos.getZ()));
        return result;
    }
    static Map<String,Object> run(ServerLevel level) {
        var pos = new BlockPos(-504,220,-1032);
        var chunk = level.getChunkAt(pos);
        var player = FakePlayerFactory.get(level, new GameProfile(UUID.fromString("23be32af-d42d-41cd-90da-4b0c17734461"), "HostAcceptance"));
        player.gameMode.changeGameModeForPlayer(GameType.SURVIVAL);
        player.setPos(pos.getX()+0.5,pos.getY(),pos.getZ()+2.5);
        var box = new AABB(pos).inflate(3);
        var rows = new ArrayList<Map<String,Object>>();
        var oreTarget = OreConfiguration.target(new TagMatchTest(BlockTags.STONE_ORE_REPLACEABLES), Blocks.COAL_ORE.defaultBlockState());
        var ore = new OreConfiguration(List.of(oreTarget),17,0);
        var config = (CaveCarverConfiguration) level.registryAccess().registryOrThrow(Registries.CONFIGURED_CARVER)
            .get(ResourceLocation.parse("minecraft:cave")).config();
        var generator = (NoiseBasedChunkGenerator)level.getChunkSource().getGenerator();
        var context = new CarvingContext(generator,level.registryAccess(),chunk,null,
            level.getChunkSource().randomState(),generator.generatorSettings().value().surfaceRule());
        var aquifer = Aquifer.createDisabled((x,y,z) -> new Aquifer.FluidStatus(-64,Blocks.LAVA.defaultBlockState()));
        var carver = new SingleBlockCarver();
        var referenceOre = oreFixture(level,pos,Blocks.STONE.defaultBlockState(),ore);
        require(!referenceOre.isEmpty(),"Empty reference ore feature");
        try {
            for (String name : List.of("limestone","slate","quartzite","gabbro")) {
                var block = BuiltInRegistries.BLOCK.get(ResourceLocation.parse("geologic_variation:"+name));
                require(block != Blocks.AIR,"Missing registered host "+name);
                var state = block.defaultBlockState();
                var placedOre = oreFixture(level,pos,state,ore);
                require(placedOre.equals(referenceOre),"Actual ore feature differs from vanilla host");
                require(state.is(BlockTags.STONE_ORE_REPLACEABLES),"Missing surface ore tag");
                require(!state.is(BlockTags.DEEPSLATE_ORE_REPLACEABLES),"Incorrect deep ore tag");
                require(OreFeature.canPlaceOre(state,p -> Blocks.STONE.defaultBlockState(),RandomSource.create(1),ore,oreTarget,pos.mutable()),"Ore target rejected host");
                // The exact-vanilla target intentionally does not accept a regional block.
                require(!new BlockMatchTest(Blocks.STONE).test(state,RandomSource.create(1)),"Exact block rule unexpectedly broadened");
                require(state.getDestroySpeed(level,pos)==Blocks.STONE.defaultBlockState().getDestroySpeed(level,pos),"Hardness changed");
                var drops = new LinkedHashMap<String,String>();
                for (String tool : List.of("hand","pickaxe","silk")) {
                    level.getEntitiesOfClass(ItemEntity.class,box).forEach(ItemEntity::discard);
                    level.setBlock(pos,state,3);
                    var stack = tool.equals("hand") ? ItemStack.EMPTY : new ItemStack(Items.IRON_PICKAXE);
                    if(tool.equals("silk")) stack.enchant(level.registryAccess().lookupOrThrow(Registries.ENCHANTMENT)
                        .getOrThrow(Enchantments.SILK_TOUCH),1);
                    player.setItemInHand(InteractionHand.MAIN_HAND,stack);
                    require(player.hasCorrectToolForDrops(state)==!tool.equals("hand"),"Tool requirement mismatch");
                    require(player.gameMode.destroyBlock(pos),"Survival break failed");
                    var entities = level.getEntitiesOfClass(ItemEntity.class,box);
                    String expected = tool.equals("silk") ? "geologic_variation:"+name : "geologic_variation:cobbled_"+name;
                    require(tool.equals("hand") ? entities.isEmpty() : entities.size()==1 && entities.getFirst().getItem().is(
                        BuiltInRegistries.ITEM.get(ResourceLocation.parse(expected))) && entities.getFirst().getItem().getCount()==1,"Incorrect survival drops: "+tool);
                    drops.put(tool,tool.equals("hand") ? "none" : expected);
                }
                level.setBlock(pos.below(),Blocks.BEDROCK.defaultBlockState(),3);
                player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(block));
                var used = player.getMainHandItem().useOn(new UseOnContext(player,InteractionHand.MAIN_HAND,
                    new BlockHitResult(Vec3.atCenterOf(pos.below()).add(0,0.5,0),Direction.UP,pos.below(),false)));
                require(used.consumesAction() && level.getBlockState(pos).is(block),"Player item placement failed");
                require(carver.one(context,config,chunk,level,pos,aquifer),"Carver rejected host");
                require(level.getBlockState(pos).isAir(),"Carver did not create cavity");
                rows.add(Map.of("host",name,"survival_drops",drops,"item_placement",true,"carved_to_air",true,
                    "coal_target",true,"exact_stone_target",false,"placed_coal_blocks",placedOre.size(),"ore_positions_match_stone",true));
            }
            var excluded = new ArrayList<String>();
            for (var block : BuiltInRegistries.BLOCK) {
                var key = BuiltInRegistries.BLOCK.getKey(block);
                if(!key.getNamespace().equals("geologic_variation")) continue;
                String name = key.getPath();
                var state = block.defaultBlockState();
                boolean natural = List.of("limestone","slate","quartzite","gabbro").contains(name);
                require(state.is(BlockTags.STONE_ORE_REPLACEABLES)==natural,"Masonry ore eligibility mismatch");
                require(!state.is(BlockTags.DEEPSLATE_ORE_REPLACEABLES),"Current surface family entered deep ore tag");
                require(state.is(config.replaceable)==natural,"Masonry carver eligibility mismatch");
                if(!natural) excluded.add(name);
            }
            require(excluded.size()==60,"Incomplete masonry exclusion coverage");
            var featureRules = new ArrayList<String>();
            for(var entry:level.registryAccess().registryOrThrow(Registries.CONFIGURED_FEATURE).entrySet()) {
                if(!(entry.getValue().config() instanceof OreConfiguration configured)) continue;
                boolean stoneEligible = configured.targetStates.stream().anyMatch(t -> t.target.test(Blocks.STONE.defaultBlockState(),RandomSource.create(1)));
                if(!stoneEligible) continue;
                for(String name:List.of("limestone","slate","quartzite","gabbro")) {
                    var state = BuiltInRegistries.BLOCK.get(ResourceLocation.parse("geologic_variation:"+name)).defaultBlockState();
                    require(configured.targetStates.stream().anyMatch(t -> t.target.test(state,RandomSource.create(1))),"Configured ore rule excludes "+name+": "+entry.getKey());
                }
                featureRules.add(entry.getKey().location().toString());
            }
            require(!featureRules.isEmpty(),"No loaded surface ore rules tested");
            return Map.of("kind","hosts","position",List.of(pos.getX(),pos.getY(),pos.getZ()),"families",rows,
                "excluded_masonry",excluded,"configured_ore_rules",featureRules);
        } finally {
            level.getEntitiesOfClass(ItemEntity.class,box).forEach(ItemEntity::discard);
            player.discard();
        }
    }
    private static List<String> oreFixture(ServerLevel level,BlockPos pos,BlockState host,OreConfiguration config) {
        // A contained uniform host volume makes vanilla and each regional host directly comparable.
        for(var p:BlockPos.betweenClosed(pos.offset(-7,-7,-7),pos.offset(7,7,7))) level.setBlock(p,host,2);
        boolean placed = new ConfiguredFeature<>(Feature.ORE,config).place(level,level.getChunkSource().getGenerator(),RandomSource.create(17),pos);
        var result = new ArrayList<String>();
        for(var p:BlockPos.betweenClosed(pos.offset(-7,-7,-7),pos.offset(7,7,7)))
            if(level.getBlockState(p).is(Blocks.COAL_ORE)) result.add((p.getX()-pos.getX())+","+(p.getY()-pos.getY())+","+(p.getZ()-pos.getZ()));
        require(placed,"Actual ore feature placed no ore");
        // Clear space for survival breaking and item placement, separate from ore placement.
        for(var p:BlockPos.betweenClosed(pos.offset(-1,-1,-1),pos.offset(1,2,3))) level.setBlock(p,Blocks.AIR.defaultBlockState(),2);
        return result;
    }
    private static final class SingleBlockCarver extends CaveWorldCarver {
        SingleBlockCarver() { super(CaveCarverConfiguration.CODEC); }
        boolean one(CarvingContext context,CaveCarverConfiguration config,net.minecraft.world.level.chunk.ChunkAccess chunk,
                    ServerLevel level,BlockPos pos,Aquifer aquifer) {
            return super.carveBlock(context,config,chunk,level::getBiome,new CarvingMask(chunk.getHeight(),chunk.getMinBuildHeight()),
                pos.mutable(),pos.below().mutable(),aquifer,new MutableBoolean(false));
        }
    }
}
