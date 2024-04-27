from multi_vector_simulator.utils.constants import *

TESTS_ON_MASTER = "master"
TESTS_ON_DEV = "dev"

EXECUTE_TESTS_ON = os.environ.get("EXECUTE_TESTS_ON", "skip")

TEST_REPO_PATH = os.path.dirname(__file__)

DUMMY_CSV_PATH = os.path.join(TEST_REPO_PATH, "test_data")

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# path of the file created automatically by
JSON_CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS, CSV_FNAME)

# folder to store input directory for tests
TEST_INPUT_DIRECTORY = "test_data"

# Folder for all benchmark test inputs:
BENCHMARK_TEST_INPUT_FOLDER = "benchmark_test_inputs"

# Folder for benchmark test outputs:
BENCHMARK_TEST_OUTPUT_FOLDER = "benchmark_test_outputs"
