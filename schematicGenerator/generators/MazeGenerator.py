import random
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
from schematicGenerator.block_palettes import *
from schematicGenerator.utils import *
import mcschematic


class MazeGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a 2D maze with 2x2 cells, ensuring no diagonal walls",
        author="ChatGPT",
        category="Structure",
    )

    DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    CELL_SIZE = 2

    @classmethod
    def generate(
        cls,
        width: int = IntInput(
            min_value=3, max_value=64, description="Width of the maze in cells", default=7
        ),
        height: int = IntInput(
            min_value=3, max_value=64, description="Height of the maze in cells", default=7
        ),
        wall_block: str = BlockInput(
            default='minecraft:black_concrete', description="Block type for the maze walls", palette=colored_solid_blocks
        ),
        path_block: str = BlockInput(
            default='minecraft:white_concrete', description="Block type for the maze path", palette=colored_solid_blocks
        )
    ) -> mcschematic.MCSchematic:
        block_width = width * cls.CELL_SIZE + 1
        block_height = height * cls.CELL_SIZE + 1
        maze = mcschematic.MCSchematic()
        
        for x in range(block_width):
            for z in range(block_height):
                maze.setBlock((x, 0, z), path_block)
        for x in range(block_width):
            maze.setBlock(((x, 0, 0)), wall_block)
            maze.setBlock((x, 0, block_height - 1), wall_block)
        for z in range(block_height):
            maze.setBlock((0, 0, z), wall_block)
            maze.setBlock((block_width - 1, 0, z), wall_block)

        for x in range(1, block_width - 1):
            for z in range(1, block_height - 1):
                if x % cls.CELL_SIZE == 0 or z % cls.CELL_SIZE == 0:
                    maze.setBlock((x, 0, z), wall_block)    

        cells = [[0 for _ in range(height)] for _ in range(width)]
        path = []
        x, z = 0, 0
        cells[x][z] = 1
        path.append((x, z))
        def is_valid_cell(x, z, width, height):
            return x >= 0 and x < width and z >= 0 and z < height and cells[x][z] == 0

        def get_neighbors(x, z, width, height):
            neighbors = []
            for dx, dz in cls.DIRECTIONS:
                print(x, z, dx, dz)
                nx, nz = x + dx, z + dz
                if is_valid_cell(nx, nz, width, height) and cells[nx][nz] == 0:
                    neighbors.append((nx, nz))
            return neighbors

        def get_wall_between_cells(x1, z1, x2, z2, cell_size):
            if x2 == x1 + 1:
                return ((x1 + 1) * cell_size, 0, z1 * cell_size + 1)
            elif x2 == x1 - 1:
                return ((x1) * cell_size, 0, z1 * cell_size + 1)
            elif z2 == z1 + 1:
                return (x1 * cell_size + 1, 0, (z1 + 1) * cell_size)
            elif z2 == z1 - 1:
                return (x1 * cell_size + 1, 0, z1 * cell_size)
            else:
                raise ValueError("Cells are not adjacent")
            
        while path:
            if not path:
                break
            x, z = path[-1]
            neighbors = get_neighbors(x, z, width, height)
            if neighbors:
                nx, nz = random.choice(neighbors)
                maze.setBlock(get_wall_between_cells(x, z, nx, nz, cls.CELL_SIZE), path_block)
                cells[nx][nz] = 1
                path.append((nx, nz))
            else:
                path.pop()

        
                

        return maze