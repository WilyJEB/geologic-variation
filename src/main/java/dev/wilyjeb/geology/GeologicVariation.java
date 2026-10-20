package dev.wilyjeb.geology;
import dev.wilyjeb.geology.domain.Provinces.Stone;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.WallBlock;
import java.util.function.Supplier;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;
@Mod(GeologicVariation.ID)
public final class GeologicVariation {
    public static final String ID = "geologic_variation";
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ID);
    public static final Map<Stone, DeferredBlock<Block>> STONES = new EnumMap<>(Stone.class);
    public static final Map<String, DeferredBlock<? extends Block>> MASONRY = new LinkedHashMap<>();
    static {
        for (Stone stone : Stone.values()) {
            String name = stone.id();
            Block host = stone.layer() == dev.wilyjeb.geology.domain.Provinces.Layer.DEEP
                    ? Blocks.DEEPSLATE : Blocks.STONE;
            var raw = cube(name, host);
            STONES.put(stone, raw);
            familyShapes(name, raw);
            familyShapes("cobbled_" + name, cube("cobbled_" + name,
                    stone.layer() == dev.wilyjeb.geology.domain.Provinces.Layer.DEEP
                            ? Blocks.COBBLED_DEEPSLATE : Blocks.COBBLESTONE));
            familyShapes("polished_" + name, cube("polished_" + name, host));
            familyShapes(name + "_bricks", cube(name + "_bricks", host));
        }
    }
    private static DeferredBlock<Block> cube(String name, Block template) {
        var block = BLOCKS.registerSimpleBlock(name, BlockBehaviour.Properties.ofFullCopy(template));
        item(name, block);
        return block;
    }
    private static void item(String name, DeferredBlock<? extends Block> block) {
        MASONRY.put(name, block);
        ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
    }
    private static void familyShapes(String name, DeferredBlock<Block> base) {
        // Singular brick shape IDs follow vanilla naming.
        String prefix = name.endsWith("_bricks") ? name.substring(0, name.length() - 1) : name;
        shape(prefix + "_stairs", () -> new StairBlock(base.get().defaultBlockState(),
                BlockBehaviour.Properties.ofFullCopy(base.get())));
        shape(prefix + "_slab", () -> new SlabBlock(BlockBehaviour.Properties.ofFullCopy(base.get())));
        shape(prefix + "_wall", () -> new WallBlock(BlockBehaviour.Properties.ofFullCopy(base.get()).forceSolidOn()));
    }
    private static <T extends Block> void shape(String name, Supplier<T> supplier) {
        item(name, BLOCKS.register(name, supplier));
    }
    public GeologicVariation(IEventBus bus) {
        BLOCKS.register(bus); ITEMS.register(bus);
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(
                (net.neoforged.neoforge.event.server.ServerStoppedEvent event) -> Geology.clearCache());
        bus.addListener(GeologicVariation::creative);
    }
    private static void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey().equals(CreativeModeTabs.BUILDING_BLOCKS))
            MASONRY.values().forEach(b -> event.accept(b.get()));
    }
}
