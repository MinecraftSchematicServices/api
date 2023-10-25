import random
import math
from schematicGenerator.inputs import IntInput, BoolInput, BlockInput, InputGroup, SelectInput
from schematicGenerator.base_generator import BaseGenerator, GeneratorMetaData
from schematicGenerator.block_palettes import *
from schematicGenerator.utils import *
import mcschematic

class DisjointSet:
    def __init__(self, nodes):
        self.parents = {node: node for node in nodes}
        self.ranks = {node: 0 for node in nodes}

    def find(self, node):
        if self.parents[node] != node:
            self.parents[node] = self.find(self.parents[node])  # path compression
        return self.parents[node]

    def union(self, node1, node2):
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 != root2:
            if self.ranks[root1] > self.ranks[root2]:
                self.parents[root2] = root1
            else:
                self.parents[root1] = root2
                if self.ranks[root1] == self.ranks[root2]:
                    self.ranks[root2] += 1

class maze_node:
    def __init__(self, position: tuple):
        self.position = position
        self.neighbours = []
        self.visited = False

    def __lt__(self, other):
        return self.position < other.position  

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)


class maze_edges:
    def __init__(self, cell_1: maze_node, cell_2: maze_node):
        self.cell_1 = cell_1
        self.cell_2 = cell_2


class maze_graph:
    def __init__(self):
        # each node uses a hash of its position as a key
        self.nodes = {}
        self.edges = {}

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_node(self, position: tuple) -> maze_node:
        return self.nodes[hash(position)]

    def get_edge(self, cell_1: maze_node, cell_2: maze_node) -> maze_edges:
        return self.edges[hash((cell_1, cell_2))]

    def get_neighbours(self, node: maze_node) -> list:
        return node.neighbours

    def get_unvisited_neighbours(self, node: maze_node) -> list:
        return [
            neighbour
            for neighbour in self.get_neighbours(node)
            if not neighbour.visited
        ]

    def get_random_unvisited_neighbour(self, node: maze_node) -> maze_node:
        return random.choice(self.get_unvisited_neighbours(node))

    def get_random_unvisited_neighbour_with_path(self, node: maze_node) -> tuple:
        neighbour = self.get_random_unvisited_neighbour(node)
        return (node, neighbour)

    def generate_maze_recursive_backtracker(self, start_node: maze_node):
        stack = [start_node]
        while stack:
            current_node = stack.pop()
            current_node.visited = True
            if self.get_unvisited_neighbours(current_node):
                stack.append(current_node)
                neighbour = self.get_random_unvisited_neighbour(current_node)
                neighbour.visited = True
                stack.append(neighbour)
                self.edges[hash((current_node, neighbour))] = maze_edges(
                    current_node, neighbour
                )


    def generate_maze_prim(self, start_node: maze_node):
        start_node.visited = True
        walls = set(tuple(sorted([start_node, neighbour])) for neighbour in self.get_neighbours(start_node))
        while walls:
            wall = random.choice(list(walls))  # Convert set to list for random choice
            walls.remove(wall)
            node1, node2 = wall
            
            # Check if only one of the two cells (node1 and node2) is visited
            if node1.visited != node2.visited:
                # Identify the unvisited node
                unvisited_node = node2 if node1.visited else node1
                
                # Mark the unvisited node as visited
                unvisited_node.visited = True
                
                # Add the edge between node1 and node2
                self.edges[hash((node1, node2))] = maze_edges(node1, node2)
                
                # Add the neighboring walls of the unvisited node to the walls set
                for neighbour in self.get_unvisited_neighbours(unvisited_node):
                    walls.add(tuple(sorted([unvisited_node, neighbour])))

    def generate_maze_kruskal(self, start_node: maze_node):
        ds = DisjointSet(self.nodes.values())
        walls = [(node, neighbour) for node in self.nodes.values() for neighbour in self.get_neighbours(node)]
        random.shuffle(walls)
        for wall in walls:
            node1, node2 = wall
            if ds.find(node1) != ds.find(node2):
                self.edges[hash(wall)] = maze_edges(node1, node2)
                ds.union(node1, node2)


    def generate_maze_hunt_and_kill(self, start_node: maze_node):
        current_node = start_node
        current_node.visited = True
        while True:
            # Kill Phase
            if self.get_unvisited_neighbours(current_node):
                neighbour = self.get_random_unvisited_neighbour(current_node)
                neighbour.visited = True
                self.edges[hash((current_node, neighbour))] = maze_edges(
                    current_node, neighbour
                )
                current_node = neighbour
            # Hunt Phase
            else:
                found = False  # A flag to check if we've found a node during the Hunt phase
                for node in self.nodes.values():
                    if not node.visited:
                        visited_neighbours = [n for n in self.get_neighbours(node) if n.visited]
                        if visited_neighbours:
                            current_node = node
                            current_node.visited = True
                            # Connect to a randomly chosen visited neighbor
                            chosen_neighbour = random.choice(visited_neighbours)
                            self.edges[hash((current_node, chosen_neighbour))] = maze_edges(
                                current_node, chosen_neighbour
                            )
                            found = True
                            break
                if not found:
                    break





def get_2d_maze_graph(width: int, height: int) -> maze_graph:
    graph = maze_graph()
    for x in range(width):
        for y in range(height):
            graph.nodes[hash((x, y))] = maze_node((x, y))
    for x in range(width):
        for y in range(height):
            node = graph.nodes[hash((x, y))]
            if x > 0:
                node.add_neighbour(graph.nodes[hash((x - 1, y))])
            if x < width - 1:
                node.add_neighbour(graph.nodes[hash((x + 1, y))])
            if y > 0:
                node.add_neighbour(graph.nodes[hash((x, y - 1))])
            if y < height - 1:
                node.add_neighbour(graph.nodes[hash((x, y + 1))])
    return graph


def get_3d_maze_graph(width: int, height: int, depth: int) -> maze_graph:
    graph = maze_graph()
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                graph.nodes[hash((x, y, z))] = maze_node((x, y, z))
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                node = graph.nodes[hash((x, y, z))]
                if x > 0:
                    node.add_neighbour(graph.nodes[hash((x - 1, y, z))])
                if x < width - 1:
                    node.add_neighbour(graph.nodes[hash((x + 1, y, z))])
                if y > 0:
                    node.add_neighbour(graph.nodes[hash((x, y - 1, z))])
                if y < height - 1:
                    node.add_neighbour(graph.nodes[hash((x, y + 1, z))])
                if z > 0:
                    node.add_neighbour(graph.nodes[hash((x, y, z - 1))])
                if z < depth - 1:
                    node.add_neighbour(graph.nodes[hash((x, y, z + 1))])
    return graph


class MazeGenerator(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Generates a 2D maze with 2x2 cells, ensuring no diagonal walls",
        author="ChatGPT",
        category="Structure",
    )
    def maze_to_world_position(maze_position: tuple, cell_size: dict = { "width": 2, "height": 2, "depth": 2 }) -> tuple:
        # the times 2 is because for each cell there is a wall, so the cell size is doubled
        return (
            maze_position[0] * cell_size["width"] * 2,
            maze_position[1] * cell_size["height"] * 2,
            maze_position[2] * cell_size["depth"] * 2,
        )

    @classmethod
    def generate(
        cls,
        maze_dimensions: dict = InputGroup(
            inputs={
                "width": IntInput(
                    min_value=3,
                    max_value=64,
                    description="Width of each cell in the maze",
                    default=10,
                ),
                "height": IntInput(
                    min_value=1,
                    max_value=64,
                    description="Height of each cell in the maze",
                    default=1,
                ),
                "depth": IntInput(
                    min_value=3,
                    max_value=64,
                    description="Depth of each cell in the maze",
                    default=10,
                ),
            },
            description="Size of each cell in the maze",
        ),
        cell_size: dict = InputGroup(
            inputs={
                "width": IntInput(
                    min_value=1,
                    max_value=64,
                    description="Width of each cell in the maze",
                    default=1,
                ),
                "height": IntInput(
                    min_value=1,
                    max_value=64,
                    description="Height of each cell in the maze",
                    default=1,
                ),
                "depth": IntInput(
                    min_value=1,
                    max_value=64,
                    description="Depth of each cell in the maze",
                    default=1,
                ),
            },
            description="Size of each cell in the maze",
        ),
        wall_block: str = BlockInput(
            default="minecraft:black_concrete",
            description="Block type for the maze walls",
            palette=(colored_blocks + invisible_blocks),
        ),
        path_block: str = BlockInput(
            default="minecraft:white_concrete",
            description="Block type for the maze path",
            palette=(colored_blocks + invisible_blocks),
        ),
        outside_block: str = BlockInput(
            default="minecraft:black_concrete",
            description="Block type for the maze outside",
            palette=(colored_blocks + invisible_blocks),
        ),
        algorithm: str = SelectInput(
            default="recursive_backtracker",
            description="Algorithm to use for maze generation",
            options=[
                "recursive_backtracker",
                "prim",
                "kruskal",
                "hunt_and_kill"
            ],
        ),
        hello_there: int = IntInput(
            min_value=0,
            max_value=1000000,
            description="A random int input",
            default=12,
        ),
    ) -> mcschematic.MCSchematic:
        


        graph = get_3d_maze_graph(
            maze_dimensions["width"],
            maze_dimensions["height"],
            maze_dimensions["depth"],
        )
        algos = {
            "recursive_backtracker": graph.generate_maze_recursive_backtracker,
            "prim": graph.generate_maze_prim,
            "kruskal": graph.generate_maze_kruskal,
            "hunt_and_kill": graph.generate_maze_hunt_and_kill,
        }
        world_dimensions = cls.maze_to_world_position(
            (
                maze_dimensions["width"],
                maze_dimensions["height"],
                maze_dimensions["depth"],
            ),
            cell_size
        )
        
        algos[algorithm](graph.nodes[hash((0, 0, 0))])
        maze = mcschematic.MCSchematic()
        for point in volume(
            (-1, -1, -1),
            (world_dimensions[0]-1, world_dimensions[1]-1, world_dimensions[2]-1),
        ):
            maze.setBlock(point if maze_dimensions["height"] > 1 else (point[0], 0, point[2]), outside_block)
        for point in volume(
            (0, 0, 0),
            (world_dimensions[0] - 2 * cell_size["width"], world_dimensions[1] - 2 * cell_size["height"], world_dimensions[2] - 2 * cell_size["depth"]),
        ):
            maze.setBlock(point, wall_block)



        cell_size_over_2 = (
            math.floor(cell_size["width"] / 2),
            math.floor(cell_size["height"] / 2),
            math.floor(cell_size["depth"] / 2),
        )

        print(cell_size_over_2)

        for edge in graph.edges.values():
            for point in bresenham_line_3d(
                cls.maze_to_world_position(edge.cell_1.position, cell_size),
                cls.maze_to_world_position(edge.cell_2.position, cell_size)
            ):
                for sub_point in volume(
                    (
                        point[0] - cell_size_over_2[0],
                        point[1] - cell_size_over_2[1],
                        point[2] - cell_size_over_2[2],
                    ),
                    (
                        point[0] + cell_size_over_2[0],
                        point[1] + cell_size_over_2[1],
                        point[2] + cell_size_over_2[2],
                    ),
                ):
                    maze.setBlock(sub_point, path_block)

        return maze
