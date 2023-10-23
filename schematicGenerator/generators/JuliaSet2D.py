import math
from schematicGenerator.inputs import (
    IntInput,
    BoolInput,
    BlockInput,
    StringInput,
    ComplexInput,
    ArrayInput,
)
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic
import numpy as np


class JuliaSetGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a Julia Set fractal",
        author="Assistant",
        category="Fractal",
        tags=["julia", "fractal"],
    )

    @classmethod
    def generate(
        cls,
        set_position: tuple = ComplexInput(
            real_low_bound=-2,
            real_high_bound=2,
            imag_low_bound=-2,
            imag_high_bound=2,
            real_default=-0.7,
            imag_default=0.27015,
            description="Complex constant c for the Julia Set",
        ),
        iterations: int = IntInput(
            min_value=1, max_value=1000, description="Number of iterations", default=30
        ),
        width: int = IntInput(
            min_value=1, max_value=2000, description="Width of the image", default=100
        ),
        height: int = IntInput(
            min_value=1, max_value=2000, description="Height of the image", default=100
        ),
        blocks: list = ArrayInput(
            default=[
                "minecraft:white_wool",
                "minecraft:orange_wool",
                "minecraft:magenta_wool",
                "minecraft:light_blue_wool",
                "minecraft:yellow_wool",
                "minecraft:lime_wool",
                "minecraft:pink_wool",
                "minecraft:gray_wool",
                "minecraft:light_gray_wool",
                "minecraft:cyan_wool",
                "minecraft:purple_wool",
                "minecraft:blue_wool",
                "minecraft:brown_wool",
                "minecraft:green_wool",
                "minecraft:red_wool",
                "minecraft:black_wool",
            ],
            description="Blocks (wool colors) to use for the image",
            element_type=BlockInput(
                description="Block",
                palette=[
                    "minecraft:white_wool",
                    "minecraft:orange_wool",
                    "minecraft:magenta_wool",
                    "minecraft:light_blue_wool",
                    "minecraft:yellow_wool",
                    "minecraft:lime_wool",
                    "minecraft:pink_wool",
                    "minecraft:gray_wool",
                    "minecraft:light_gray_wool",
                    "minecraft:cyan_wool",
                    "minecraft:purple_wool",
                    "minecraft:blue_wool",
                    "minecraft:brown_wool",
                    "minecraft:green_wool",
                    "minecraft:red_wool",
                    "minecraft:black_wool",
                ],
            ),
            min_length=2,
            max_length=16,
        ),
    ) -> mcschematic.MCSchematic:
        schem = mcschematic.MCSchematic()

        # Define the x and y ranges to visualize
        x = np.linspace(-2, 2, width)
        y = np.linspace(-2, 2, height)

        output = np.zeros((width, height))

        for x_idx, x_val in enumerate(x):
            for y_idx, y_val in enumerate(y):
                z = complex(x_val, y_val)
                count = 0
                for _ in range(iterations):
                    if abs(z) > 2:
                        break
                    z = z * z + set_position
                    count += 1
                output[x_idx, y_idx] = count

        num_colors = len(blocks)
        color_step = iterations / num_colors

        for x_idx in range(width):
            for y_idx in range(height):
                color_idx = int(output[x_idx, y_idx] / color_step)
                color_idx = min(
                    color_idx, num_colors - 1
                )  # Ensure the index is within the range
                schem.setBlock((x_idx, 0, y_idx), blocks[color_idx])

        return schem
