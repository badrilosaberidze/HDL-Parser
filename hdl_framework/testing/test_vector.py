"""
Test vector representation for HDL chip testing.
"""

from typing import Dict


class TestVector:

    def __init__(self, inputs: Dict[str, int], outputs: Dict[str, int]):
        self.inputs = inputs
        self.outputs = outputs

    def get_input(self, pin_name: str) -> int:
        return self.inputs.get(pin_name, 0)

    def get_expected_output(self, pin_name: str) -> int:
        return self.outputs.get(pin_name, 0)

    def get_all_inputs(self) -> Dict[str, int]:
        return self.inputs.copy()

    def get_all_expected_outputs(self) -> Dict[str, int]:
        return self.outputs.copy()

    def input_pins(self) -> list:
        return list(self.inputs.keys())

    def output_pins(self) -> list:
        return list(self.outputs.keys())

    def __str__(self):
        input_str = ', '.join([f"{k}={v}" for k, v in self.inputs.items()])
        output_str = ', '.join([f"{k}={v}" for k, v in self.outputs.items()])
        return f"Inputs: {input_str} | Expected: {output_str}"

    def __repr__(self):
        return f"TestVector(inputs={self.inputs}, outputs={self.outputs})"

    def __eq__(self, other):
        if not isinstance(other, TestVector):
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs

    def __hash__(self):
        return hash((tuple(sorted(self.inputs.items())), tuple(sorted(self.outputs.items()))))