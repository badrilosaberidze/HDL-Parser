import argparse
import sys
import os
from pathlib import Path

from hdl_framework.parser import HDLParser
from hdl_framework.testing import TestRunner

def test_chip(hdl_file: str, test_file: str, hdl_path: str = "hdl_files"):
    """Test a single chip with its test file"""
    try:
        parser = HDLParser(base_path=hdl_path)

        print(f"Parsing HDL file: {hdl_file}")
        chip = parser.parse_file(hdl_file)
        print(f"Successfully parsed chip: {chip.name}")
        print(f"Inputs: {chip.inputs}")
        print(f"Outputs: {chip.outputs}")
        print()

        runner = TestRunner(chip)

        print(f"Loading test file: {test_file}")
        test_vectors = runner.parse_test_file(test_file)
        print(f"Found {len(test_vectors)} test cases")
        print()

        results = runner.run_all_tests(test_vectors)

        return results["success_rate"] == 1.0

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_all_chips(hdl_path: str = "hdl_files", test_path: str = "hdl_test_files"):
    """Test all chips in the hdl_files directory"""
    hdl_dir = Path(hdl_path)
    test_dir = Path(test_path)

    if not hdl_dir.exists():
        print(f"HDL directory '{hdl_path}' not found")
        return False

    if not test_dir.exists():
        print(f"Test directory '{test_path}' not found")
        return False

    hdl_files = list(hdl_dir.glob("*.hdl"))

    if not hdl_files:
        print(f"No HDL files found in '{hdl_path}'")
        return False

    print(f"Found {len(hdl_files)} HDL files")
    print("=" * 60)

    results = []
    for hdl_file in hdl_files:
        chip_name = hdl_file.stem
        test_file = test_dir / f"{chip_name}.csv"

        if test_file.exists():
            print(f"\nTesting {chip_name}...")
            success = test_chip(chip_name, str(test_file), hdl_path)
            results.append((chip_name, success))
        else:
            print(f"No test file found for {chip_name} (expected: {test_file})")
            results.append((chip_name, None))

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success is True)
    failed = sum(1 for _, success in results if success is False)
    skipped = sum(1 for _, success in results if success is None)
    total = len(results)

    for chip_name, success in results:
        if success is True:
            print(f"{chip_name} - PASSED")
        elif success is False:
            print(f"{chip_name} - FAILED")
        else:
            print(f"⚠{chip_name} - SKIPPED (no test file)")

    print(f"\nTotal: {total} chips")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    if failed == 0 and passed > 0:
        print("\nAll tested chips passed!")
        return True
    elif failed > 0:
        print(f"\n{failed} chips failed")
        return False
    else:
        print("\nNo chips were tested")
        return False


def interactive_mode():
    """Interactive mode for testing chips"""
    print("HDL Framework - Interactive Mode")
    print("=" * 40)

    while True:
        print("\nOptions:")
        print("1. Test a single chip")
        print("2. Test all chips")
        print("3. List available chips")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            hdl_path = input("HDL files directory [hdl_files]: ").strip() or "hdl_files"
            chip_name = input("Chip name (without .hdl): ").strip()
            test_file = input("Test file path: ").strip()

            if chip_name and test_file:
                test_chip(chip_name, test_file, hdl_path)
            else:
                print("Please provide both chip name and test file")

        elif choice == "2":
            hdl_path = input("HDL files directory [hdl_files]: ").strip() or "hdl_files"
            test_path = input("Test files directory [tests]: ").strip() or "tests"
            test_all_chips(hdl_path, test_path)

        elif choice == "3":
            hdl_path = input("HDL files directory [hdl_files]: ").strip() or "hdl_files"
            hdl_dir = Path(hdl_path)

            if hdl_dir.exists():
                hdl_files = list(hdl_dir.glob("*.hdl"))
                if hdl_files:
                    print(f"\nAvailable chips in '{hdl_path}':")
                    for hdl_file in sorted(hdl_files):
                        print(f"  - {hdl_file.stem}")
                else:
                    print(f"No HDL files found in '{hdl_path}'")
            else:
                print(f"Directory '{hdl_path}' not found")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-4.")


def create_example_files():
    """Create example project structure"""
    print("Creating example project structure...")

    os.makedirs("hdl_files", exist_ok=True)
    os.makedirs("hdl_test_files", exist_ok=True)

    # Create example And.hdl
    and_hdl = """// And gate implementation using NAND
                CHIP And {
                    IN a, b;
                    OUT out;
                
                    PARTS:
                    Nand(a=a, b=b, out=nandOut);
                    Not(in=nandOut, out=out);
                }"""

    # Create example And.tst
    and_tst = """a,b,out
                0,0,0
                0,1,0
                1,0,0
                1,1,1"""

    with open("hdl_files/And.hdl", "w") as f:
        f.write(and_hdl)

    with open("hdl_test_files/And.csv", "w") as f:
        f.write(and_tst)

    print("  Created example files:")
    print("  - hdl_files/And.hdl")
    print("  - hdl_test_files/And.csv")
    print("\nYou can now run: python main.py test And hdl_test_files/And.csv")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="HDL Parser and Chip Testing Framework",
        epilog="Examples:\n"
               "  python main.py test And tests/And.tst\n"
               "  python main.py test-all\n"
               "  python main.py interactive\n"
               "  python main.py create-examples",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test single chip command
    test_parser = subparsers.add_parser("test", help="Test a single chip")
    test_parser.add_argument("chip", help="Chip name (without .hdl extension)")
    test_parser.add_argument("test_file", help="Path to test file")
    test_parser.add_argument("--hdl-path", default="hdl_files",
                             help="Directory containing HDL files (default: hdl_files)")

    # Test all chips command
    test_all_parser = subparsers.add_parser("test-all", help="Test all chips")
    test_all_parser.add_argument("--hdl-path", default="hdl_files",
                                 help="Directory containing HDL files (default: hdl_files)")
    test_all_parser.add_argument("--test-path", default="tests",
                                 help="Directory containing test files (default: tests)")

    # Interactive mode command
    subparsers.add_parser("interactive", help="Run in interactive mode")

    # Create examples command
    subparsers.add_parser("create-examples", help="Create example project structure")

    args = parser.parse_args()

    if args.command == "test":
        success = test_chip(args.chip, args.test_file, args.hdl_path)
        sys.exit(0 if success else 1)

    elif args.command == "test-all":
        success = test_all_chips(args.hdl_path, args.test_path)
        sys.exit(0 if success else 1)

    elif args.command == "interactive":
        interactive_mode()

    elif args.command == "create-examples":
        create_example_files()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()