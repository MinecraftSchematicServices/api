import math
import os
from math import log
import mcschematic
import numpy as np
import sympy as sp
from schematic_generator.inputs import (
    IntInput,
    BlockInput,
    ArrayInput,
)
from schematic_generator.base_generator import BaseGenerator, GeneratorMetaData
from schematic_generator.block_palettes import *

class NewtonFractalGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description= open(os.path.dirname(os.path.realpath(__file__)) + "/description.md", "r").read(),
        author="User",
        category="Fractal",
        tags=["newton", "fractal"],
    )

    @classmethod
    def generate(
        cls,
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
            default=colored_wool_palette,
            description="Blocks (wool colors) to use for the image",
            element_type=BlockInput(
                description="Block",
                palette=colored_solid_blocks
            ),
            min_length=2,
            max_length=16,
        ),
    ) -> mcschematic.MCSchematic:
        z = sp.symbols('z')
        fx_str = "z**3 - 1"
        fx = sp.sympify(fx_str)
        d_fx = sp.diff(fx, z)
        d_fx_str = str(d_fx)
        print(fx_str, d_fx_str)
        schem = mcschematic.MCSchematic()
        x = np.linspace(-2, 2, width)
        y = np.linspace(-2, 2, height)
        output = np.zeros((width, height), dtype=int)
        roots = [complex(1, 0), complex(-0.5, math.sqrt(3)/2), complex(-0.5, -math.sqrt(3)/2)]  # Roots of z**3 - 1
        for x_idx, x_val in enumerate(x):
            for y_idx, y_val in enumerate(y):
                z = complex(x_val, y_val)
                for i in range(iterations):
                    try:
                        z -= eval(fx_str) / eval(d_fx_str)
                    except ZeroDivisionError:
                        break
                    for root_idx, root in enumerate(roots):
                        if abs(z - root) < 0.01:
                            output[x_idx, y_idx] = root_idx + 1
                            break
                    if output[x_idx, y_idx] > 0:
                        break
        num_colors = len(blocks)
        print(output)
        for x_idx in range(width):
            for y_idx in range(height):
                color_idx = output[x_idx, y_idx] - 1
                if color_idx >= 0:
                    schem.setBlock((x_idx, 0, y_idx), blocks[color_idx])
        print("done")
        return schem
