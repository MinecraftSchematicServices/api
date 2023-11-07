import math
from schematic_generator.inputs import IntInput, BoolInput, BlockInput
from schematic_generator.base_generator import BaseGenerator, GeneratorMetaData
from schematic_generator.block_palettes import *
try:
    import mcschematic
    import numpy as np
except Exception as e:
    print(e)
    pass

class Test(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Test",
        author="Nano",
        category="Test",
    )
    @classmethod
    def generate(
        cls,

    ) -> mcschematic.MCSchematic:
        print("Generating")
        schem: mcschematic.MCSchematic = mcschematic.MCSchematic() 
        # schem.setBlock((0, 0, 0), "minecraft:cyan_concrete")
        schem.setBlock((0, 1, 0), "minecraft:redstone_wire[east=side,north=none,power=0,south=side,west=side]")
        # water block to the left of the redstone wire
        # schem.setBlock((-1, 1, 0), "minecraft:water[level=0]")
        # schem.setBlock((1, 0, 0), "minecraft:red_concrete")
        # schem.setBlock((0, 1, 0), "minecraft:lime_concrete")
        # schem.setBlock((0, 1, 0), "minecraft:comparator[facing=west,mode=subtract,powered=true]")
        # schem.setBlock((1,0,0), "minecraft:gray_concrete")
        # schem.setBlock((1,1,0), "minecraft:redstone_wire[east=side,north=none,power=2,south=none,west=side]")
        # schem.setBlock((0, 1, 1), "minecraft:redstone_torch[lit=true]")
        # schem.setBlock((0, 1, 4), "minecraft:dispenser[facing=east,triggered=true]")
        # schem.setBlock((0, 1, 3), "minecraft:dropper[facing=east,triggered=true]")
        # schem.setBlock((0, 1, 1), "minecraft:observer[facing=east,powered=true]")

        

        # schem.setBlock((0, 0, 0), "minecraft:gray_concrete")

        
        return schem