"""
Composite chip implementation for chips built from other chips and gates.
"""

from typing import Dict, List, Tuple, Optional
from .gate import Gate
from ..utils.connections import Connection


class CompositeChip(Gate):

    def __init__(self, name: str, inputs: List[str], outputs: List[str]):
        super().__init__(name, inputs, outputs)
        self.sub_chips: Dict[str, Gate] = {}
        self.internal_connections: List[Connection] = []
        self.input_connections: Dict[str, List[Tuple[str, str]]] = {}  # input_pin -> [(chip_name, pin_name)]
        self.output_connections: Dict[str, Tuple[str, str]] = {}  # output_pin -> (chip_name, pin_name)

    def add_sub_chip(self, instance_name: str, chip: Gate):
        self.sub_chips[instance_name] = chip

    def add_input_connection(self, input_pin: str, target_chip: str, target_pin: str):
        if input_pin not in self.input_connections:
            self.input_connections[input_pin] = []
        self.input_connections[input_pin].append((target_chip, target_pin))

    def add_output_connection(self, output_pin: str, source_chip: str, source_pin: str):
        self.output_connections[output_pin] = (source_chip, source_pin)

    def add_internal_connection(self, source_chip: str, source_pin: str, target_chip: str, target_pin: str):
        connection = Connection(source_chip, source_pin, target_chip, target_pin)
        self.internal_connections.append(connection)

    def compute(self) -> Dict[str, int]:
        for input_pin, value in self.input_values.items():
            if input_pin in self.input_connections:
                for chip_name, pin_name in self.input_connections[input_pin]:
                    if chip_name in self.sub_chips:
                        self.sub_chips[chip_name].set_input(pin_name, value)

        max_iterations = 10
        for iteration in range(max_iterations):
            changed = False

            for chip in self.sub_chips.values():
                old_outputs = chip.output_values.copy()
                chip.compute()
                if chip.output_values != old_outputs:
                    changed = True

            for conn in self.internal_connections:
                if conn.source_chip in self.sub_chips and conn.target_chip in self.sub_chips:
                    source_chip = self.sub_chips[conn.source_chip]
                    target_chip = self.sub_chips[conn.target_chip]

                    if conn.source_pin in source_chip.outputs:
                        value = source_chip.get_output(conn.source_pin)
                        target_chip.set_input(conn.target_pin, value)

            if not changed:
                break

        for output_pin in self.outputs:
            if output_pin in self.output_connections:
                chip_name, pin_name = self.output_connections[output_pin]
                if chip_name in self.sub_chips:
                    self.output_values[output_pin] = self.sub_chips[chip_name].get_output(pin_name)

        return self.output_values

    def reset(self):
        super().reset()
        for chip in self.sub_chips.values():
            chip.reset()

    def get_sub_chip(self, instance_name: str) -> Optional[Gate]:
        return self.sub_chips.get(instance_name)

    def list_sub_chips(self) -> List[str]:
        return list(self.sub_chips.keys())

    def get_connection_info(self) -> Dict:
        return {
            "input_connections": self.input_connections,
            "output_connections": self.output_connections,
            "internal_connections": [str(conn) for conn in self.internal_connections],
            "sub_chips": list(self.sub_chips.keys())
        }