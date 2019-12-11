try:
    from .F1_plotting import plots
except ImportError:
    from code_folder.F1_plotting import plots

import json
import numpy
import pandas as pd
import logging
import matplotlib.pyplot as plt


class output_processing:
    def evaluate_dict(dict_values):
        logging.info(
            "Summarizing simulation results to results_timeseries and results_scalars_assets."
        )
        for sector in dict_values["project_data"]["sectors"]:
            sector_name = dict_values["project_data"]["sectors"][sector]
            total_demand = pd.Series(
                [0 for i in dict_values["simulation_settings"]["time_index"]],
                index=dict_values["simulation_settings"]["time_index"],
            )

            for asset in dict_values["energyConsumption"][sector_name]:
                total_demand = (
                    total_demand
                    + dict_values["energyConsumption"][sector_name][asset]["flow"]
                )

            # todo this should actually link to C0: helpers.bus_suffix
            dict_values["optimizedFlows"][sector_name + " bus"][
                "Total demand " + sector_name
            ] = total_demand

            plots.flows(
                dict_values["simulation_settings"],
                dict_values["project_data"],
                dict_values["optimizedFlows"][sector_name + " bus"],
                sector,
                14,
            )
            plots.flows(
                dict_values["simulation_settings"],
                dict_values["project_data"],
                dict_values["optimizedFlows"][sector_name + " bus"],
                sector,
                365,
            )

        helpers.store_timeseries_all_busses_to_excel(dict_values)

        print('-----')
        print('capacities')
        print(dict_values["kpi"]["scalar_matrix"]["optimizedAddCap"].values)
        print('annuities')
        print(dict_values["kpi"]["cost_matrix"]["annuity_total"].values)
        print('investment')
        print(dict_values["kpi"]["cost_matrix"]["costs_investment"].values)
        print('om')
        print(dict_values["kpi"]["cost_matrix"]["costs_om"].values)
        # plot the capacities and the annuity costs
        show_optimal_capacities = False
        for element in dict_values["kpi"]["scalar_matrix"]["optimizedAddCap"].values:
            if element > 0:
                show_optimal_capacities = True
        if show_optimal_capacities:
            plots.capacities(
                dict_values["simulation_settings"],
                dict_values["project_data"],
                dict_values["kpi"]["cost_matrix"]["label"],
                dict_values["kpi"]["scalar_matrix"]["optimizedAddCap"],
            )

        plots.costs(dict_values)


        # Write everything to file with multipe tabs
        results_scalar_output_file = "/scalars" + ".xlsx"
        with pd.ExcelWriter(
            dict_values["simulation_settings"]["path_output_folder"]
            + results_scalar_output_file
        ) as open_file:  # doctest: +SKIP
            for kpi_set in dict_values["kpi"]:
                if isinstance(dict_values["kpi"][kpi_set], dict):
                    data = pd.DataFrame([dict_values["kpi"][kpi_set]]).to_excel(
                        open_file, sheet_name=kpi_set
                    )
                else:
                    dict_values["kpi"][kpi_set].to_excel(open_file, sheet_name=kpi_set)
                logging.info(
                    "Saved scalar results to: %s, tab %s.",
                    results_scalar_output_file,
                    kpi_set,
                )
        return


class helpers:
    def store_timeseries_all_busses_to_excel(dict_values):
        # todo this should be moved to f0_output
        timeseries_output_file = "/timeseries_all_busses" + ".xlsx"
        with pd.ExcelWriter(
            dict_values["simulation_settings"]["path_output_folder"]
            + timeseries_output_file
        ) as open_file:  # doctest: +SKIP
            for bus in dict_values["optimizedFlows"]:
                dict_values["optimizedFlows"][bus].to_excel(open_file, sheet_name=bus)
                dict_values["optimizedFlows"][bus].plot()
                plt.savefig(
                    dict_values["simulation_settings"]["path_output_folder"]
                    + "/"
                    + bus
                    + " flows.png",
                    bbox_inches="tight",
                )
                # if bus == 'Electricity (LES) bus' or bus == 'Electricity (DSO) bus':
                #    plt.show()
                plt.close()
                plt.clf()
                plt.cla()

        logging.info("Saved flows at busses to: %s.", timeseries_output_file)
        return

    def store_as_json(dict_values, file_name):
        # This converts all data stored in dict_values that is not compatible with the json format to a format that is compatible.
        def convert(o):
            if isinstance(o, numpy.int64):
                return int(o)
            # todo this actually drops the date time index, which could be interesting
            if isinstance(o, pd.DatetimeIndex):
                return "date_range"
            if isinstance(o, pd.datetime):
                return str(o)
            # todo this also drops the timeindex, which is unfortunate.
            if isinstance(o, pd.Series):
                return "pandas timeseries"  # o.values
            if isinstance(o, numpy.ndarray):
                return "numpy timeseries"  # o.tolist()
            if isinstance(o, pd.DataFrame):
                return "pandas dataframe"  # o.to_json(orient='records')
            logging.error(
                "An error occurred when converting the simulation data (dict_values) to json, as the type is not recognized: \n"
                "Type: " + str(type(o)) + " \n"
                "Value(s): " + str(o) + "\n"
                "Please edit function CO_data_processing.dataprocessing.store_as_json."
            )
            raise TypeError

        file_path = (
            dict_values["simulation_settings"]["path_output_folder"]
            + "/"
            + file_name
            + ".json"
        )
        myfile = open(file_path, "w")
        json_data = json.dumps(
            dict_values, skipkeys=True, sort_keys=True, default=convert, indent=4
        )
        myfile.write(json_data)
        myfile.close()
        logging.info(
            "Converted and stored processed simulation data to json: %s", file_path
        )
        return
