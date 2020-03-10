import timeit
import logging
import oemof.solph as solph
import oemof.outputlib as outputlib


import src.D1_model_components as model_components


def run_oemof(dict_values):
    """
    Creates and solves energy system model generated from excel template inputs.
    Each component is included by calling its constructor function in D1_model_components.

    :param dict values: Includes all dictionary values describing the whole project, including costs,
                        technical parameters and components. In C0_data_processing, each component was attributed
                        with a certain in/output bus.

    :return: saves and returns oemof simulation results
    """

    # Start clock to determine total simulation time
    start = timeit.default_timer()

    logging.info("Initializing oemof simulation.")
    model = solph.EnergySystem(
        timeindex=dict_values["simulation_settings"]["time_index"]
    )

    # this dictionary will include all generated oemof objects
    dict_model = {
        "busses": {},
        "sinks": {},
        "sources": {},
        "transformers": {},
        "storages": {},
    }

    logging.info("Adding components to energy system model...")

    # Check all dict values and if necessary call component
    # "for loop" chosen to raise errors in case entries are not defined
    # other way would be: if key in dict_values: define/call component
    for bus in dict_values["energyBusses"]:
        model_components.bus(model, bus, **dict_model)

    def warning_asset_type(asset, type, assetGroup):
        """

        :param asset:
        :param type:
        :param assetGroup:
        :return:
        """
        logging.error(
            "Asset %s has type %s, "
            "but this type is not an asset type attributed to asset group %s for oemof model generation.",
            asset,
            type,
            assetGroup,
        )
        return

    for asset in dict_values["energyConversion"]:
        type = dict_values["energyConversion"][asset]["type_oemof"]
        if type == "transformer":
            model_components.transformer(
                model, dict_values["energyConversion"][asset], **dict_model
            )
        else:
            warning_asset_type(asset, type, "energyConversion")

    for asset in dict_values["energyConsumption"]:
        type = dict_values["energyConsumption"][asset]["type_oemof"]
        if type == "sink":
            model_components.sink(
                model, dict_values["energyConsumption"][asset], **dict_model
            )
        else:
            warning_asset_type(asset, type, "energyConsumption")

    for asset in dict_values["energyProduction"]:

        type = dict_values["energyProduction"][asset]["type_oemof"]
        if type == "source":
            model_components.source(
                model, dict_values["energyProduction"][asset], **dict_model
            )
        else:
            warning_asset_type(asset, type, "energyProduction")

    for asset in dict_values["energyStorage"]:
        type = dict_values["energyStorage"][asset]["type_oemof"]
        if type == "storage":
            model_components.storage(
                model, dict_values["energyStorage"][asset], **dict_model
            )
        else:
            warning_asset_type(asset, type, "energyStorage")

    logging.debug("All components added.")

    if dict_values["simulation_settings"]["plot_nx_graph"]["value"] == True:
        import oemof.graph as grph

        my_graph = grph.create_nx_graph(model, filename="my_graph.xml")
        from src.F1_plotting import draw_graph

        draw_graph(model, node_color={})
        logging.debug("Created networkx graph of the energy system.")

    logging.debug("Creating oemof model based on created components and busses...")
    local_energy_system = solph.Model(model)
    logging.debug("Created oemof model based on created components and busses.")

    logging.info("Adding constraints to oemof model...")
    # todo include constraints
    """
    Stability constraint
    include constraint linking two converters (ie "in/out")
    Minimal renewable share constraint
    """
    logging.debug("All constraints added.")

    if dict_values["simulation_settings"]["output_lp_file"]["value"] == True:
        logging.debug("Saving to lp-file.")
        local_energy_system.write(
            dict_values["simulation_settings"]["path_output_folder"] + "/lp_file.lp",
            io_options={"symbolic_solver_labels": True},
        )

    logging.info("Starting simulation.")
    local_energy_system.solve(
        solver="cbc",
        solve_kwargs={
            "tee": False
        },  # if tee_switch is true solver messages will be displayed
        cmdline_options={"ratioGap": str(0.03)},
    )  # ratioGap allowedGap mipgap
    logging.info("Problem solved.")

    # add results to the energy system to make it possible to store them.
    results_main = outputlib.processing.results(local_energy_system)
    results_meta = outputlib.processing.meta_results(local_energy_system)

    model.results["main"] = results_main
    model.results["meta"] = results_meta

    # store energy system with results
    if dict_values["simulation_settings"]["store_oemof_results"]["value"] == True:
        model.dump(
            dpath=dict_values["simulation_settings"]["path_output_folder"],
            filename=dict_values["simulation_settings"]["oemof_file_name"],
        )
        logging.debug(
            "Stored results in %s/MVS_results.oemof.",
            dict_values["simulation_settings"]["path_output_folder"],
        )

    duration = timeit.default_timer() - start

    dict_values.update(
        {
            "simulation_results": {
                "label": "simulation_results",
                "objective_value": results_meta["objective"],
                "simulation_time": results_meta["solver"]["Time"],
                "modelling_time": duration,
            }
        }
    )

    logging.info(
        "Simulation time: %s minutes.",
        round(dict_values["simulation_results"]["simulation_time"] / 60, 2),
    )
    logging.info(
        "Moddeling time: %s minutes.",
        round(dict_values["simulation_results"]["modelling_time"] / 60, 2),
    )

    return results_meta, results_main  # , dict_model
