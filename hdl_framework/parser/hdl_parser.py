"""
HDL file parser that converts HDL files into Gate objects.
"""

import re
import os
from typing import Dict, List, Tuple
from ..core.gate import Gate
from ..core.builtin_gates import create_builtin_gate, is_builtin_gate
from ..core.composite_chip import CompositeChip


class HDLParser:

    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.parsed_chips: Dict[str, Gate] = {}

    def parse_file(self, filename: str) -> Gate:
        cache_key = filename.replace('.hdl', '')

        if cache_key in self.parsed_chips:
            return self.parsed_chips[cache_key]

        if filename.endswith('.hdl'):
            filepath = os.path.join(self.base_path, filename)
        else:
            filepath = os.path.join(self.base_path, filename + '.hdl')

        with open(filepath, 'r') as file:
            content = file.read()

        chip = self._parse_hdl_content(content, cache_key)
        self.parsed_chips[cache_key] = chip
        return chip

    def _parse_hdl_content(self, content: str, filename: str) -> Gate:
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = ' '.join(content.split())

        chip_match = re.search(r'CHIP\s+(\w+)', content)
        if not chip_match:
            raise ValueError(f"No CHIP declaration found in {filename}")
        chip_name = chip_match.group(1)

        in_match = re.search(r'IN\s+([^;]+);', content)
        inputs = []
        if in_match:
            inputs = [pin.strip() for pin in in_match.group(1).split(',')]

        out_match = re.search(r'OUT\s+([^;]+);', content)
        outputs = []
        if out_match:
            outputs = [pin.strip() for pin in out_match.group(1).split(',')]

        chip = CompositeChip(chip_name, inputs, outputs)

        parts_match = re.search(r'PARTS:\s*(.*)', content, re.DOTALL)
        if parts_match:
            parts_content = parts_match.group(1).strip()
            self._parse_parts_section(parts_content, chip)

        return chip

    def _parse_parts_section(self, parts_content: str, chip: CompositeChip):
        part_instances = re.findall(r'(\w+)\s*\(([^)]+)\);', parts_content)

        instance_counter = {}
        all_connections = []

        for part_type, connections_str in part_instances:
            if part_type not in instance_counter:
                instance_counter[part_type] = 0
            instance_name = f"{part_type}_{instance_counter[part_type]}"
            instance_counter[part_type] += 1

            if is_builtin_gate(part_type):
                sub_chip = create_builtin_gate(part_type)
            else:
                template = self.parse_file(part_type)
                if isinstance(template, CompositeChip):
                    sub_chip = self._create_chip_copy(template)
                else:
                    gate_type = template.__class__.__name__.replace('Gate', '')
                    if is_builtin_gate(gate_type):
                        sub_chip = create_builtin_gate(gate_type)
                    else:
                        sub_chip = template

            chip.add_sub_chip(instance_name, sub_chip)

            connections = [conn.strip() for conn in connections_str.split(',')]
            for connection in connections:
                if '=' in connection:
                    pin_name, wire_name = connection.split('=')
                    pin_name = pin_name.strip()
                    wire_name = wire_name.strip()
                    all_connections.append((instance_name, sub_chip, pin_name, wire_name))

        self._process_connections(all_connections, chip)

    def _create_chip_copy(self, template: CompositeChip) -> CompositeChip:
        sub_chip = CompositeChip(template.name, template.inputs[:], template.outputs[:])

        for sub_name, sub_gate in template.sub_chips.items():
            if isinstance(sub_gate, CompositeChip):
                sub_chip.sub_chips[sub_name] = self._create_chip_copy(sub_gate)
            else:
                gate_type = sub_gate.__class__.__name__.replace('Gate', '')
                if is_builtin_gate(gate_type):
                    sub_chip.sub_chips[sub_name] = create_builtin_gate(gate_type)
                else:
                    sub_chip.sub_chips[sub_name] = sub_gate

        sub_chip.internal_connections = template.internal_connections[:]
        sub_chip.input_connections = {k: v[:] for k, v in template.input_connections.items()}
        sub_chip.output_connections = template.output_connections.copy()

        return sub_chip

    def _process_connections(self, all_connections, chip: CompositeChip):
        wire_connections: Dict[str, List[Tuple[str, str, bool]]] = {}

        for instance_name, sub_chip, pin_name, wire_name in all_connections:
            if wire_name not in wire_connections:
                wire_connections[wire_name] = []

            is_output = pin_name in sub_chip.outputs
            wire_connections[wire_name].append((instance_name, pin_name, is_output))

        for wire_name, connections in wire_connections.items():
            outputs = [(inst, pin) for inst, pin, is_out in connections if is_out]
            inputs = [(inst, pin) for inst, pin, is_out in connections if not is_out]

            if wire_name in chip.inputs:
                for inst_name, pin_name in inputs:
                    chip.add_input_connection(wire_name, inst_name, pin_name)
            elif wire_name in chip.outputs:
                if outputs:
                    inst_name, pin_name = outputs[0]
                    chip.add_output_connection(wire_name, inst_name, pin_name)
            else:
                if outputs and inputs:
                    source_inst, source_pin = outputs[0]
                    for target_inst, target_pin in inputs:
                        chip.add_internal_connection(source_inst, source_pin, target_inst, target_pin)

    def get_parsed_chips(self) -> Dict[str, Gate]:
        return self.parsed_chips.copy()

    def clear_cache(self):
        self.parsed_chips.clear()