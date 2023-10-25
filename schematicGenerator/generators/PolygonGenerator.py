import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput, ArrayInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic
from schematicGenerator.block_palettes import *
import random
import math
from schematicGenerator.utils import bresenham_line_2d

class PolygonGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a regular polygon with a given number of sides and radius",
        author="ChatGPT",
        category="Shape",
    )

    @classmethod
    def generate(
        cls,
        sides: int = IntInput(
            min_value=3, max_value=18, description="Number of sides of the polygon", default=5
        ),
        radius: int = IntInput(
            min_value=1, max_value=128, description="The radius of the polygon", default=20
        ),
        filled: bool = BoolInput(
            default=False, description="Whether the polygon should be filled or not"
        ),
        inner_blocks: list = ArrayInput(
            default=[],
            description="The blocks to use for the inner part of the polygon",
            element_type=BlockInput(
                description="Block",
                palette=colored_solid_blocks
            ),
            min_length=0,
            max_length=16,
        ),
        border_blocks: list = ArrayInput(
            default=['minecraft:white_concrete'],
            description="The blocks to use for the border of the polygon",
            element_type=BlockInput(
                description="Block",
                palette=colored_solid_blocks
            ),
            min_length=1,
            max_length=16,
        ),
        height: int = IntInput(
            min_value=1, max_value=128, description="The height of the polygon", default=1
        ),
    ) -> mcschematic.MCSchematic:
        schem = mcschematic.MCSchematic()
        if len(inner_blocks) == 0:
            inner_blocks = border_blocks

        vertices = [
            (
                int(radius * math.cos(2 * math.pi * k / sides)),
                int(radius * math.sin(2 * math.pi * k / sides))
            )
            for k in range(sides)
        ]

        # Draw or fill the polygon using the vertices
        for i in range(height):
            if filled:
                # Fill the polygon using a scanline algorithm or other technique
                for x in range(-radius, radius + 1):
                    for z in range(-radius, radius + 1):
                        if is_point_inside_polygon((x, z), vertices):
                            # Choose an inner block at random
                            block_choice = random.choice(inner_blocks)
                            schem.setBlock((x + radius, i, z + radius), block_choice)
            
            for k in range(sides):
                start_vertex = vertices[k]
                end_vertex = vertices[(k + 1) % sides]
                for point in bresenham_line_2d(start_vertex, end_vertex):
                    # Choose a border block at random
                    block_choice = random.choice(border_blocks)
                    schem.setBlock((point[0] + radius, i, point[1] + radius), block_choice)

        return schem


def is_point_inside_polygon(point, vertices):
    # Use a point-in-polygon algorithm to determine if the point is inside the polygon
    # Here, we'll use the ray casting method
    x, y = point
    odd_nodes = False
    j = len(vertices) - 1

    for i in range(len(vertices)):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        if yi < y and yj >= y or yj < y and yi >= y:
            if xi + (y - yi) / (yj - yi) * (xj - xi) < x:
                odd_nodes = not odd_nodes
        j = i

    return odd_nodes


