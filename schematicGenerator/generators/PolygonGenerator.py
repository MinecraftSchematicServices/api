import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic


import math

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
            min_value=3, max_value=12, description="Number of sides of the polygon", default=7
        ),
        radius: int = IntInput(
            min_value=1, max_value=128, description="The radius of the polygon", default=5
        ),
        filled: bool = BoolInput(
            default=True, description="Whether the polygon should be filled or not"
        ),
        block: list = BlockInput(
            default="minecraft:white_concrete",
            description="The block to use for the polygon",
        ),
        height: int = IntInput(
            min_value=1, max_value=128, description="The height of the polygon", default=1
        ),
    ) -> mcschematic.MCSchematic:
        schem = mcschematic.MCSchematic()

        # Calculate the vertices of the polygon
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
                            schem.setBlock((x + radius, i, z + radius), block)
            else:
                # Draw only the outline of the polygon
                for k in range(sides):
                    start_vertex = vertices[k]
                    end_vertex = vertices[(k + 1) % sides]
                    for point in bresenham_line(start_vertex, end_vertex):
                        schem.setBlock((point[0] + radius, i, point[1] + radius), block)

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

def bresenham_line(start, end):
    # Bresenham's line algorithm to generate points between two vertices
    points = []
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points
