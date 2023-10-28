import math
import os
from schematic_generator.inputs import IntInput, BoolInput, BlockInput, InputGroup, SelectInput
from schematic_generator.base_generator import BaseGenerator, GeneratorMetaData
from schematic_generator.generators.PolygonGenerator import PolygonGenerator
import mcschematic

BASE_SCHEMATIC_PATH = os.path.dirname(os.path.realpath(__file__))+ "/component_schematics/"
FIRST_HALF_ADDER_PATH = BASE_SCHEMATIC_PATH + "first_half_adder.schem"
SECOND_HALF_ADDER_PATH = BASE_SCHEMATIC_PATH + "second_half_adder.schem"

class Adder(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Adder",
        author="Nano ",
        category="Computational",
        tags=["Adder", "Math", "Computational"],
    )
    @classmethod
    def generate(
        cls,
        adder_bits: int = IntInput(
            min_value=1,
            max_value=64,
            description="The number of bits in the adder",
            default=8,
        ),
    ) -> mcschematic.MCSchematic:
        adder: mcschematic.MCSchematic = mcschematic.MCSchematic()
        first_half_adder: mcschematic.MCSchematic = mcschematic.MCSchematic(schematicToLoadPath_or_mcStructure=FIRST_HALF_ADDER_PATH)
        second_half_adder: mcschematic.MCSchematic = mcschematic.MCSchematic(schematicToLoadPath_or_mcStructure=SECOND_HALF_ADDER_PATH)
        polygon_base = PolygonGenerator.generate(sides=8, radius=20, filled=True, border_blocks=["minecraft:white_concrete"], inner_blocks=["minecraft:cyan_concrete"])
        for i in range(0, adder_bits):
            offset_second_half_adder = (i // 8) * 4
            adder.placeSchematic(first_half_adder, (0, i*2, 0))
            adder.placeSchematic(second_half_adder, (5 + offset_second_half_adder, i*2, 0))
        adder.placeSchematic(polygon_base, (-14, -1, -20))
        return adder
        