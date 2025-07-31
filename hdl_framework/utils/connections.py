"""
Data classes for representing connections and chip instances in HDL files.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Connection:
    source_chip: str
    source_pin: str
    target_chip: str
    target_pin: str

    def __str__(self):
        return f"{self.source_chip}.{self.source_pin} -> {self.target_chip}.{self.target_pin}"

    def __repr__(self):
        return self.__str__()


@dataclass
class ChipInstance:
    name: str
    chip_type: str
    connections: Dict[str, str] = field(default_factory=dict)

    def add_connection(self, pin_name: str, wire_name: str):
        self.connections[pin_name] = wire_name

    def get_connection(self, pin_name: str) -> str:
        return self.connections.get(pin_name, "")

    def __str__(self):
        connections_str = ", ".join([f"{pin}={wire}" for pin, wire in self.connections.items()])
        return f"{self.chip_type} {self.name}({connections_str})"

    def __repr__(self):
        return self.__str__()