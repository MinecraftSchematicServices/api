import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput, StringInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic


class SquareGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a square of a given side length and block",
        author="Sloimy   ",
        categories=["shapes"],
    )
    @classmethod
    def generate(
        cls,
        side_length: int = IntInput(
            min_value=1, max_value=128, description="The side length of the square"
        ),
        filled: bool = BoolInput(
            default=True, description="Whether the square should be filled or not"
        ),
        block: list = BlockInput(
            default="minecraft:white_concrete",
            description="The block to use for the square",
        ),
    ) -> mcschematic.MCSchematic:
        print("Generating")
        schem: mcschematic.MCSchematic = mcschematic.MCSchematic()
        for x in range(-side_length, side_length + 1):
            for z in range(-side_length, side_length + 1):
                if filled:
                    schem.setBlock((x + side_length, 0, z + side_length), block)
                else:
                    if side_length - 1 <= x <= side_length + 1 and side_length - 1 <= z <= side_length + 1:
                        schem.setBlock((x + side_length, 0, z + side_length), block)
        return schem