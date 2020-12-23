from multi_vector_simulator.cli import main

if __name__ == "__main__":
    main(
        overwrite=True,
        input_type="csv",
        path_input_folder="tests/benchmark_test_inputs/Feature_parameters_as_timeseries",
        save_png=True,
        pdf_report=True,
    )
