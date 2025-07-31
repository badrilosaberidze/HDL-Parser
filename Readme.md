# HDL Parser and Chip Testing Framework

A comprehensive HDL (Hardware Description Language) parser and chip testing framework for the Nand2Tetris course. This tool parses HDL files, builds internal chip representations, simulates digital logic, and automatically verifies chip behavior against test vectors.

## Features

- **HDL File Parsing**: Parse syntactically correct HDL files with `IN`, `OUT`, and `PARTS` sections
- **Built-in Gates**: Native support for `Nand`, `Not`, `And`, and `Or` gates
- **Recursive Chip Loading**: Automatically loads and parses dependent chip files
- **Logic Simulation**: Accurately simulates digital logic behavior
- **Automated Testing**: Run test vectors and generate detailed pass/fail reports
- **CLI Interface**: Easy-to-use command-line tools
- **Modular Architecture**: Clean, extensible codebase with type annotations

## Requirements

- Python 3.8+
- No external dependencies required

## Installation

1. **Clone or download the project**:
   ```bash
   git clone https://github.com/badrilosaberidze/HDL-Parser
   cd HDL-parser
   ```

2. **Set up the project structure**:
   ```
   HDL-parser/
   ├── hdl_framework/          # Main framework package
   ├── main.py                 # CLI entry point
   ├── hdl_files/              # Your HDL chip files (.hdl)
   ├── hdl_test_files/         # Your test vector files (.csv)
   ```

3. **Create example files** (optional):
   ```bash
   python main.py create-examples
   ```

## Quick Start

### Basic Usage

```bash
# Test a single chip
python main.py test Xor hdl_test_files/Xor.tst

# Test all chips in your project
python main.py test-all

# Interactive mode
python main.py interactive
```

### Python API Usage

```python
from hdl_framework import HDLParser, TestRunner

# Parse an HDL file
parser = HDLParser(base_path="hdl_files")
chip = parser.parse_file("Xor")

# Run tests
runner = TestRunner(chip)
test_vectors = runner.parse_test_file("hdl_test_files/Xor.tst")
results = runner.run_all_tests(test_vectors)
```

## Usage Guide

### Command Line Interface

The framework provides several CLI commands:

#### 1. Test Single Chip
```bash
python main.py test <chip_name> <test_file> [--hdl-path HDL_PATH]
```

**Parameters:**
- `chip_name`: Name of the chip (without .hdl extension)
- `test_file`: Path to the test vector file
- `--hdl-path`: Directory containing HDL files (default: hdl_files)

**Example:**
```bash
python main.py test Mux hdl_test_files/Mux.tst --hdl-path my_hdl_files
```

#### 2. Test All Chips
```bash
python main.py test-all [--hdl-path HDL_PATH] [--test-path TEST_PATH]
```

**Parameters:**
- `--hdl-path`: Directory containing HDL files (default: hdl_files)
- `--test-path`: Directory containing test files (default: tests)

**Example:**
```bash
python main.py test-all --hdl-path chips --test-path test_vectors
```

#### 3. Interactive Mode
```bash
python main.py interactive
```

Provides a menu-driven interface for:
- Testing individual chips
- Running batch tests
- Listing available chips

#### 4. Create Example Files
```bash
python main.py create-examples
```

Creates sample HDL and test files to get you started.

## Built-in Components

### Built-in Gates

The framework includes these primitive gates:

| Gate | Inputs | Outputs | Description |
|------|---------|---------|-------------|
| `Nand` | a, b | out | Logical NAND gate |
| `Not` | in | out | Logical NOT gate |
| `And` | a, b | out | Logical AND gate |
| `Or` | a, b | out | Logical OR gate |

### Custom Chips

Any chip not in the built-in list must have a corresponding `.hdl` file. The framework:
1. Automatically finds and parses the HDL file
2. Recursively loads any dependent chips
3. Builds an internal simulation model
4. Integrates it into the parent chip

## 🧪 Testing and Validation

### Test Output Format

```
Running 4 test cases for Xor:
------------------------------------------------------------
Test  1: PASS | Inputs: a=0, b=0 | Expected: out=0
Test  2: PASS | Inputs: a=0, b=1 | Expected: out=1
Test  3: PASS | Inputs: a=1, b=0 | Expected: out=1
Test  4: PASS | Inputs: a=1, b=1 | Expected: out=0
------------------------------------------------------------
Summary: 4/4 tests passed
🎉 All tests passed!
```

### Test Results

For each test case, the framework shows:
- **Test number**: Sequential test identifier
- **Status**: PASS or FAIL
- **Inputs**: All input pin values
- **Expected outputs**: Expected values from test file
- **Actual outputs**: Computed values (shown only on failure)

## 📚 Examples

### Example HDL Files

**And Gate Implementation:**
```hdl
CHIP And {
    IN a, b;
    OUT out;

    PARTS:
    Nand(a=a, b=b, out=nandOut);
    Not(in=nandOut, out=out);
}
```

**Multiplexer Implementation:**
```hdl
CHIP Mux {
    IN a, b, sel;
    OUT out;

    PARTS:
    Not(in=sel, out=notSel);
    And(a=a, b=notSel, out=aAndNotSel);
    And(a=b, b=sel, out=bAndSel);
    Or(a=aAndNotSel, b=bAndSel, out=out);
}
```

### Example Test Files

**And Gate Tests:**
```csv
a,b,out
0,0,0
0,1,0
1,0,0
1,1,1
```

**Multiplexer Tests:**
```csv
a,b,sel,out
0,0,0,0
0,0,1,0
0,1,0,0
0,1,1,1
1,0,0,1
1,0,1,0
1,1,0,1
1,1,1,1
```

**Happy chip building!**