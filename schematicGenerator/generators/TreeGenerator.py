import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput, StringInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
try:
    import mcschematic
    import numpy as np
    print(np.zeros((3,3)))
except Exception as e:
    print(e)
    pass

class TreeGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a tree of a given height and block",
        author="Sloimy",
        category="Vegetation",
    )
    @classmethod
    def generate(
        cls,
        height: int = IntInput(
            min_value=1, max_value=128, description="The height of the tree"
        ),
        filled: bool = BoolInput(
            default=True, description="Whether the tree should be filled or not"
        ),
        block: list = BlockInput(
            palette=["minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves", "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves"],
            default="minecraft:oak_leaves",
            description="The block to use for the tree",
        ),
    ) -> mcschematic.MCSchematic:
        print("Generating")
        schem: mcschematic.MCSchematic = mcschematic.MCSchematic()
        for x in range(-height, height + 1):
            for z in range(-height, height + 1):
                if filled:
                    schem.setBlock((x + height, 0, z + height), block)
                else:
                    if height - 1 <= x <= height + 1 and height - 1 <= z <= height + 1:
                        schem.setBlock((x + height, 0, z + height), block)
        return schem