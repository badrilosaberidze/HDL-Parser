"""
Built-in gate implementations for the HDL framework.
These are primitive gates that don't require HDL parsing.
"""

from typing import Dict, Callable
from .gate import Gate


class NandGate(Gate):

    def __init__(self):
        super().__init__("Nand", ["a", "b"], ["out"])

    def compute(self) -> Dict[str, int]:
        a = self.input_values.get("a", 0)
        b = self.input_values.get("b", 0)
        result = 1 if not (a and b) else 0
        self.output_values["out"] = result
        return {"out": result}


class NotGate(Gate):

    def __init__(self):
        super().__init__("Not", ["in"], ["out"])

    def compute(self) -> Dict[str, int]:
        in_val = self.input_values.get("in", 0)
        result = 1 if not in_val else 0
        self.output_values["out"] = result
        return {"out": result}


class AndGate(Gate):

    def __init__(self):
        super().__init__("And", ["a", "b"], ["out"])

    def compute(self) -> Dict[str, int]:
        a = self.input_values.get("a", 0)
        b = self.input_values.get("b", 0)
        result = 1 if (a and b) else 0
        self.output_values["out"] = result
        return {"out": result}


class OrGate(Gate):

    def __init__(self):
        super().__init__("Or", ["a", "b"], ["out"])

    def compute(self) -> Dict[str, int]:
        a = self.input_values.get("a", 0)
        b = self.input_values.get("b", 0)
        result = 1 if (a or b) else 0
        self.output_values["out"] = result
        return {"out": result}


BUILTIN_GATES: Dict[str, Callable[[], Gate]] = {
    "Nand": NandGate,
    "Not": NotGate,
    "And": AndGate,
    "Or": OrGate
}


def create_builtin_gate(gate_type: str) -> Gate:
    if gate_type in BUILTIN_GATES:
        return BUILTIN_GATES[gate_type]()
    else:
        raise ValueError(f"Unknown built-in gate type: {gate_type}")


def is_builtin_gate(gate_type: str) -> bool:
    return gate_type in BUILTIN_GATES