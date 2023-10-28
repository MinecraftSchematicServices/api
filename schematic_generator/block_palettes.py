prefix = "minecraft:"
colors = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]
air = "minecraft:air"
barrier = "minecraft:barrier"
invisible_blocks = [air, barrier]
colored_wool_palette = [prefix + color + "_wool" for color in colors]
colored_concrete_palette = [prefix + color + "_concrete" for color in colors]
colored_terracotta_palette = [prefix + color + "_terracotta" for color in colors]
colored_glazed_terracotta_palette = [prefix + color + "_glazed_terracotta" for color in colors]
colored_stained_glass_palette = [prefix + color + "_stained_glass" for color in colors]
colored_stained_glass_pane_palette = [prefix + color + "_stained_glass_pane" for color in colors]
colored_solid_blocks = colored_wool_palette + colored_concrete_palette + colored_terracotta_palette + colored_glazed_terracotta_palette
colored_blocks = colored_solid_blocks + colored_stained_glass_palette