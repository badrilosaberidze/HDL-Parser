"""
Test runner for executing HDL chip tests using test vectors.
"""

from typing import List, Dict
from ..core.gate import Gate
from .test_vector import TestVector


class TestResult:

    def __init__(self, test_vector: TestVector, passed: bool, actual_outputs: Dict[str, int]):
        self.test_vector = test_vector
        self.passed = passed
        self.actual_outputs = actual_outputs

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        result = f"{status} | {self.test_vector}"
        if not self.passed:
            actual_str = ', '.join([f"{k}={v}" for k, v in self.actual_outputs.items()])
            result += f"\n        Actual: {actual_str}"
        return result


class TestRunner:

    def __init__(self, chip: Gate):
        self.chip = chip
        self.test_results: List[TestResult] = []

    def parse_test_file(self, filename: str) -> List[TestVector]:
        test_vectors: List[TestVector] = []

        with open(filename, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        if not lines:
            return test_vectors

        header = lines[0]
        all_pins = [pin.strip() for pin in header.split(',')]

        input_pins = [pin for pin in all_pins if pin in self.chip.inputs]
        output_pins = [pin for pin in all_pins if pin in self.chip.outputs]

        for line in lines[1:]:
            values = [int(val.strip()) for val in line.split(',')]

            pin_values = dict(zip(all_pins, values))

            inputs = {pin: pin_values[pin] for pin in input_pins}
            outputs = {pin: pin_values[pin] for pin in output_pins}

            test_vectors.append(TestVector(inputs, outputs))

        return test_vectors

    def run_test(self, test_vector: TestVector) -> TestResult:
        self.chip.reset()

        for pin, value in test_vector.inputs.items():
            self.chip.set_input(pin, value)

        actual_outputs = self.chip.compute()

        passed = True
        for pin, expected_value in test_vector.outputs.items():
            actual_value = actual_outputs.get(pin, 0)
            if actual_value != expected_value:
                passed = False
                break

        return TestResult(test_vector, passed, actual_outputs)

    def run_all_tests(self, test_vectors: List[TestVector], verbose: bool = True) -> Dict[str, float]:
        self.test_results.clear()
        passed_count = 0
        total_count = len(test_vectors)

        if verbose:
            print(f"Running {total_count} test cases for {self.chip.name}:")
            print("-" * 60)

        for i, test_vector in enumerate(test_vectors):
            result = self.run_test(test_vector)
            self.test_results.append(result)

            if result.passed:
                passed_count += 1

            if verbose:
                print(f"Test {i + 1:2d}: {result}")

        if verbose:
            print("-" * 60)
            print(f"Summary: {passed_count}/{total_count} tests passed")

            if passed_count == total_count:
                print("All tests passed!")
            else:
                print(f"{total_count - passed_count} tests failed")

        return {
            "total": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "success_rate": passed_count / total_count if total_count > 0 else 0
        }

    def get_failed_tests(self) -> List[TestResult]:
        return [result for result in self.test_results if not result.passed]

    def get_passed_tests(self) -> List[TestResult]:
        return [result for result in self.test_results if result.passed]

    def get_test_summary(self) -> Dict:
        total = len(self.test_results)
        passed = len(self.get_passed_tests())
        failed = len(self.get_failed_tests())

        return {
            "chip_name": self.chip.name,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": passed / total if total > 0 else 0,
            "all_passed": failed == 0
        }

    def export_results(self, filename: str):
        with open(filename, 'w') as file:
            file.write(f"Test Results for {self.chip.name}\n")
            file.write("=" * 50 + "\n\n")

            for i, result in enumerate(self.test_results):
                file.write(f"Test {i + 1}: {result}\n")

            summary = self.get_test_summary()
            file.write(f"\nSummary: {summary['passed_tests']}/{summary['total_tests']} tests passed\n")
            file.write(f"Success Rate: {summary['success_rate']:.2%}\n")