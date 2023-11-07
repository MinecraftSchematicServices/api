import math
import os
from schematic_generator.inputs import (
    IntInput,
    BoolInput,
    BlockInput,
    InputGroup,
    SelectInput,
)
from schematic_generator.base_generator import BaseGenerator, GeneratorMetaData
from schematic_generator.generators.PolygonGenerator import PolygonGenerator
from schematic_generator.generators.MazeGenerator import MazeGenerator
from schematic_generator.block_palettes import *

import mcschematic
from immutable_views import *
from typing import Union, List, Tuple, Dict

BASE_SCHEMATIC_PATH = (
    os.path.dirname(os.path.realpath(__file__)) + "/component_schematics/"
)
FIRST_HALF_ADDER_PATH = BASE_SCHEMATIC_PATH + "first_half_adder.schem"
SECOND_HALF_ADDER_PATH = BASE_SCHEMATIC_PATH + "second_half_adder.schem"
CARRY_OUT_SECOND_HALF_ADDER_PATH = (
    BASE_SCHEMATIC_PATH + "carry_out_second_half_adder.schem"
)
INTERNAL_CONNECTION_PATH = BASE_SCHEMATIC_PATH + "internal_connection.schem"
OUTPUT_SYNC_PATH = BASE_SCHEMATIC_PATH + "output_sync.schem"
MARKER_BLOCK = "minecraft:purple_concrete"
CARRY_FREQUENCY = 7


def replace_block(
    schematic: mcschematic.MCSchematic, block_to_replace: str, replacement_block: str
) -> mcschematic.MCSchematic:
    schematic = add_block_to_palette(schematic, block_to_replace)
    schematic = add_block_to_palette(schematic, replacement_block)
    structure = schematic.getStructure()
    block_palette = dict(structure.getBlockPalette())
    block_states = structure.getBlockStates()
    block_replace_index = block_palette.get(block_to_replace)
    replacement_block_index = block_palette.get(replacement_block)
    new_block_states = {
        k: v if v != block_replace_index else replacement_block_index
        for k, v in block_states.items()
    }
    structure._blockStates = new_block_states
    schematic._structure = structure
    return schematic


def add_block_to_palette(
    schematic: mcschematic.MCSchematic, block: str
) -> mcschematic.MCSchematic:
    structure = schematic.getStructure()
    block_palette = dict(structure.getBlockPalette())
    print(block_palette)
    if block_palette.get(block) is not None:
        return schematic
    block_palette[block] = len(block_palette)
    structure._blockPalette = block_palette
    schematic._structure = structure
    return schematic


def remove_markers(schematic: mcschematic.MCSchematic) -> mcschematic.MCSchematic:
    return replace_block(schematic, MARKER_BLOCK, "minecraft:air")


class Adder(BaseGenerator):
    meta_data = GeneratorMetaData(
        description="Adder",
        author="Nano",
        category="Computational",
        tags=["Adder", "Math", "Computational"],
    )

    @classmethod
    def generate(
        cls,
        adder_bits: int = IntInput(
            min_value=1,
            max_value=256,
            description="The number of bits in the adder",
            default=8,
        ),
        main_block: str = BlockInput(
            description="The main block that constitutes the adder",
            palette=colored_solid_blocks,
            default="minecraft:gray_concrete",
        ),
        highlight_block: str = BlockInput(
            description="The block that highlights the adder",
            palette=colored_solid_blocks,
            default="minecraft:lime_concrete",
        )
        
    ) -> mcschematic.MCSchematic:
        adder: mcschematic.MCSchematic = mcschematic.MCSchematic()
        first_half_adder: mcschematic.MCSchematic = mcschematic.MCSchematic(
            schematicToLoadPath_or_mcStructure=FIRST_HALF_ADDER_PATH
        )
        second_half_adder: mcschematic.MCSchematic = mcschematic.MCSchematic(
            schematicToLoadPath_or_mcStructure=SECOND_HALF_ADDER_PATH
        )
        carry_out_second_half_adder: mcschematic.MCSchematic = mcschematic.MCSchematic(
            schematicToLoadPath_or_mcStructure=CARRY_OUT_SECOND_HALF_ADDER_PATH
        )
        internal_connection: mcschematic.MCSchematic = mcschematic.MCSchematic(
            schematicToLoadPath_or_mcStructure=INTERNAL_CONNECTION_PATH
        )
        output_sync: mcschematic.MCSchematic = mcschematic.MCSchematic(
            schematicToLoadPath_or_mcStructure=OUTPUT_SYNC_PATH
        )
        remove_markers(first_half_adder)
        remove_markers(second_half_adder)
        remove_markers(carry_out_second_half_adder)
        remove_markers(internal_connection)
        remove_markers(output_sync)
        max_byte_groups = adder_bits // CARRY_FREQUENCY
        for i in range(0, adder_bits):
            byte_group = i // CARRY_FREQUENCY
            offset_second_half_adder = byte_group * 4
            adder.placeSchematic(first_half_adder, (0, i * 2, 0))
            adder.placeSchematic(
                second_half_adder, (offset_second_half_adder, i * 2, 0)
            )
            for j in range(byte_group):
                adder.placeSchematic(internal_connection, (j * 4, i * 2, 0))
            for k in range(max_byte_groups - byte_group):
                adder.placeSchematic(output_sync, ((max_byte_groups - k) * 4, i * 2, 0))
        for i in range(0, adder_bits // CARRY_FREQUENCY):
            adder.placeSchematic(
                carry_out_second_half_adder, (i * 4, (i + 1) * 2 * CARRY_FREQUENCY, 0)
            )
        if main_block != "minecraft:red_concrete":
            adder = replace_block(adder, "minecraft:gray_concrete", main_block)

        adder = replace_block(adder, "minecraft:red_concrete", highlight_block)
        if main_block == "minecraft:red_concrete":
            adder = replace_block(adder, "minecraft:gray_concrete", main_block)
        return adder
