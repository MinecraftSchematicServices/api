import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic


class PolygonGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a regular polygon with a given number of sides and radius",
        author="ChatGPT",
        categories=["shapes"],
    )

    @classmethod
    def generate(
        cls,
        sides: int = IntInput(
            min_value=3, max_value=12, description="Number of sides of the polygon"
        ),
        radius: int = IntInput(
            min_value=1, max_value=128, description="The radius of the polygon"
        ),
        filled: bool = BoolInput(
            default=True, description="Whether the polygon should be filled or not"
        ),
        block: list = BlockInput(
            default="minecraft:white_concrete",
            description="The block to use for the polygon",
        ),
    ) -> mcschematic.MCSchematic:
        schem: mcschematic.MCSchematic = mcschematic.MCSchematic()
        angle_step = 2 * math.pi / sides

        for x in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                distance = math.sqrt(x**2 + z**2)
                angle = math.atan2(z, x)
                nearest_vertex = round(angle / angle_step)
                angle_to_vertex = nearest_vertex * angle_step
                distance_to_edge = distance * math.cos(angle - angle_to_vertex)

                if filled:
                    if distance_to_edge <= radius:
                        schem.setBlock((x + radius, 0, z + radius), block)
                else:
                    if radius - 1 <= distance_to_edge <= radius + 1:
                        schem.setBlock((x + radius, 0, z + radius), block)

        return schem
