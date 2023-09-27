import math
from inputs import IntInput, BoolInput, BlockInput, StringInput
from base_generator import BaseGenerator, GeneratorMetaData
import mcschematic


class CircleGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a circle of a given radius and block",
        author="Nano",
        categories=["shapes"],
    )
    @classmethod
    def generate(
        cls,
        radius: int = IntInput(
            min_value=1, max_value=128, description="The radius of the circle"
        ),
        filled: bool = BoolInput(
            default=True, description="Whether the circle should be filled or not"
        ),
        block: list = BlockInput(
            default="minecraft:white_concrete",
            description="The block to use for the circle",
        ),
    ) -> mcschematic.MCSchematic:
        print("Generating")
        schem: mcschematic.MCSchematic = mcschematic.MCSchematic()
        for x in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                distance = math.sqrt(x**2 + z**2)
                if filled:
                    if distance <= radius:
                        schem.setBlock((x + radius, 0, z + radius), block)
                else:
                    if radius - 1 <= distance <= radius + 1:
                        schem.setBlock((x + radius, 0, z + radius), block)
        return schem
