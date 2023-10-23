import random
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
import mcschematic

class MazeGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a maze of a given width and height",
        author="ChatGPT",
        category="Maze",
    )

    @classmethod
    def generate(
        cls,
        width: int = IntInput(
            min_value=5, max_value=128, description="Width of the maze", default=15
        ),
        height: int = IntInput(
            min_value=5, max_value=128, description="Height of the maze", default=15
        ),
        block: list = BlockInput(
            default="minecraft:stone_bricks",
            description="The block to use for the maze walls",
        ),
    ) -> mcschematic.MCSchematic:
        schem = mcschematic.MCSchematic()

        # Initialize maze with all walls
        for x in range(width):
            for y in range(height):
                schem.setBlock((x, y, 0), block)

        # Stack for backtracking
        stack = []
        # Convert maze size to size in terms of cells
        cell_width = (width - 1) // 2
        cell_height = (height - 1) // 2

        # Starting point
        start_x, start_y = random.randint(0, cell_width - 1), random.randint(0, cell_height - 1)
        stack.append((start_x, start_y))

        # Directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = [[False for _ in range(cell_height)] for _ in range(cell_width)]
        visited[start_x][start_y] = True

        # Carve out starting point
        schem.setBlock((start_x * 2 + 1, start_y * 2 + 1, 0), "minecraft:air")

        while stack:
            x, y = stack[-1]
            possible_directions = []

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cell_width and 0 <= ny < cell_height and not visited[nx][ny]:
                    # Check if there are walls on both sides
                    if (schem.getBlockStateAt((nx * 2 + 1 + dx, ny * 2 + 1 + dy, 0)) is not None) and \
                       (schem.getBlockStateAt((nx * 2 + 1 - dx, ny * 2 + 1 - dy, 0)) is not None):
                        possible_directions.append((dx, dy))

            if possible_directions:
                dx, dy = random.choice(possible_directions)
                nx, ny = x + dx, y + dy
                visited[nx][ny] = True
                # Carve through walls to next cell
                schem.setBlock((x * 2 + 1 + dx, y * 2 + 1 + dy, 0), None)
                schem.setBlock((nx * 2 + 1, ny * 2 + 1, 0), None)
                stack.append((nx, ny))
            else:
                stack.pop()  # Backtrack

        return schem
