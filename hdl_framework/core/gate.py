"""
Abstract base class for all gates and chips in the HDL framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class Gate(ABC):

    def __init__(self, name: str, inputs: List[str], outputs: List[str]):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.input_values: Dict[str, int] = {}
        self.output_values: Dict[str, int] = {}

    @abstractmethod
    def compute(self) -> Dict[str, int]:
        pass

    def set_input(self, pin_name: str, value: int):
        if pin_name in self.inputs:
            self.input_values[pin_name] = value
        else:
            raise ValueError(f"Input pin '{pin_name}' not found in {self.name}")

    def get_output(self, pin_name: str) -> int:
        if pin_name in self.outputs:
            return self.output_values.get(pin_name, 0)
        else:
            raise ValueError(f"Output pin '{pin_name}' not found in {self.name}")

    def reset(self):
        self.input_values.clear()
        self.output_values.clear()

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, inputs={self.inputs}, outputs={self.outputs})"

    def __repr__(self):
        return self.__str__()