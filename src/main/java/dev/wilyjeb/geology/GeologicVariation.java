package dev.wilyjeb.geology;
import dev.wilyjeb.geology.domain.Provinces.Stone;
import java.util.EnumMap;
import java.util.Locale;
import java.util.Map;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
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
    static {
        for (Stone stone : Stone.values()) {
            String name = stone.name().toLowerCase(Locale.ROOT);
            var block = BLOCKS.registerSimpleBlock(name, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE));
            STONES.put(stone, block);
            ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
        }
    }
    public GeologicVariation(IEventBus bus) {
        BLOCKS.register(bus); ITEMS.register(bus);
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(
                (net.neoforged.neoforge.event.server.ServerStoppedEvent event) -> Geology.clearCache());
        bus.addListener(GeologicVariation::creative);
    }
    private static void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey().equals(CreativeModeTabs.BUILDING_BLOCKS))
            STONES.values().forEach(b -> event.accept(b.get()));
    }
}