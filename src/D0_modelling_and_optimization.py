import timeit
import logging
import oemof.solph as solph
import oemof.outputlib as outputlib


import src.D1_model_components as model_components

from src.constants_json_strings import ENERGY_BUSSES, OEMOF_ASSET_TYPE, ACCEPTED_ASSETS_FOR_ASSET_GROUPS, OEMOF_GEN_STORAGE, OEMOF_SINK, OEMOF_SOURCE, OEMOF_TRANSFORMER
"""
Functional requirements of module D0:
- measure time needed to build model
- measure time needed to solve model
- generate energy system model for oemof
- create dictionary of components so that they can be used for constraints and some
- raise warning if component not a (in mvs defined) oemof model type
- add all energy conversion, energy consumption, energy production, energy storage devices model
- plot network graph
- at constraints to remote model
- store lp file (optional)
- start oemof simulation
- process results by giving them to the next function
- dump oemof results
- add simulation parameters to dict values 
"""

class WrongOemofAssetForGroupError(ValueError):
    # Exception raised when an asset group has an asset with an denied oemof type
    pass

class UnknownOemofAssetType(ValueError):
    # Exception raised in case an asset type is defined for an asset group constants_json_strings but the oemof function is not jet defined (only dev)
    pass

def run_oemof(dict_values):
    """
    Creates and solves energy system model generated from excel template inputs.
    Each component is included by calling its constructor function in D1_model_components.

    :param dict values: Includes all dictionary values describing the whole project, including costs,
                        technical parameters and components. In C0_data_processing, each component was attributed
                        with a certain in/output bus.

    :return: saves and returns oemof simulation results
    """

    start = timer.initalize()

    model, dict_model = model_building.initialize(dict_values)

    model = model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)

    model_building.plot_networkx_graph(dict_values, model)

    logging.debug("Creating oemof model based on created components and busses...")
    local_energy_system = solph.Model(model)
    logging.debug("Created oemof model based on created components and busses.")

    model_building.add_constraints()

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


    dict_values.update(
        {
            "simulation_results": {
                "label": "simulation_results",
                "objective_value": results_meta["objective"],
                "simulation_time": results_meta["solver"]["Time"],
            }
        }
    )

    logging.info(
        "Simulation time: %s minutes.",
        round(dict_values["simulation_results"]["simulation_time"] / 60, 2),
    )

    timer.stop(dict_values, start)

    return results_meta, results_main

class model_building:
    def initialize(dict_values):
        '''
        Initalization of oemof model

        dict_values: dict
            dictionary of simulation

        Returns
        -------
        oemof energy model (oemof.solph.network.EnergySystem), dict_model which gathers the assets added to this model later.
        '''
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

        return model, dict_model


    def adding_assets_to_energysystem_model(dict_values, dict_model, model, **kwargs):
        '''

        Parameters
        ----------
        dict_values: dict
            dict of simulation data

        model: oemof.solph.network.EnergySystem
            Model of oemof energy system

        dict_model:
            Updated list of assets in the oemof energy system model

        Returns
        -------

        '''
        logging.info("Adding components to oemof energy system model...")

        # Busses have to be defined first
        for bus in dict_values[ENERGY_BUSSES]:
            model_components.bus(model, bus, **dict_model)

        # Adding step by step all assets defined within the asset groups
        for asset_group in ACCEPTED_ASSETS_FOR_ASSET_GROUPS:
            if asset_group in dict_values:
                for asset in dict_values[asset_group]:
                    type = dict_values[asset_group][asset][OEMOF_ASSET_TYPE]
                    # Checking if the asset type is one accepted for the asset group (security measure)
                    if type in ACCEPTED_ASSETS_FOR_ASSET_GROUPS[asset_group]:
                        # if so, then the appropriate function of D1 should be called
                        if type == OEMOF_TRANSFORMER:
                            model_components.transformer(
                                model, dict_values[asset_group][asset], **dict_model
                            )
                        elif type == OEMOF_SINK:
                            model_components.sink(
                                model, dict_values[asset_group][asset], **dict_model
                            )
                        elif type == OEMOF_SOURCE:
                            model_components.source(
                                model, dict_values[asset_group][asset], **dict_model
                            )
                        elif type == OEMOF_GEN_STORAGE:
                            model_components.storage(
                                model, dict_values[asset_group][asset], **dict_model
                            )
                        else:
                            raise UnknownOemofAssetType(
                                f"Asset {asset} has type {type}, "
                                f"but this type is not a defined oemof asset type."
                            )

                    else:
                        raise WrongOemofAssetForGroupError(
                            f"Asset {asset} has type {type}, "
                            f"but this type is not an asset type attributed to asset group {asset_group}"
                            f" for oemof model generation."
                        )

        logging.debug("All components added.")
        return model

    def plot_networkx_graph(dict_values, model):
        if (
                dict_values["simulation_settings"]["display_nx_graph"]["value"] == True
                or dict_values["simulation_settings"]["store_nx_graph"]["value"] is True
        ):
            from src.F1_plotting import draw_graph

            draw_graph(
                dict_values,
                model,
                node_color={},
                show_plot=dict_values["simulation_settings"]["display_nx_graph"]["value"],
                save_plot=dict_values["simulation_settings"]["store_nx_graph"]["value"],
                user_input=dict_values["simulation_settings"],
            )
            logging.debug("Created networkx graph of the energy system.")
        return

    def add_constraints():
        logging.info("Adding constraints to oemof model...")
        """
        Stability constraint
        include constraint linking two converters (ie "in/out")
        Minimal renewable share constraint
        """
        logging.debug("All constraints added.")
        return

class timer:
    def initalize():
        '''
        Starts a timer
        Returns
        -------
        '''
        # Start clock to determine total simulation time
        start = timeit.default_timer()
        return start

    def stop(dict_values, start):
        '''
        Ends timer and adds duration of simulation to dict_values
        Parameters
        ----------
        dict_values: dict
            Dict of simulation including "simulation_results" key
        start: timestamp
            start time of timer

        Returns
        -------
        Simulation time in dict_values
        '''
        duration = timeit.default_timer() - start
        dict_values["simulation_results"].update(
            {"modelling_time": round(duration, 2)}
        )

        logging.info(
            "Moddeling time: %s minutes.",
            round(dict_values["simulation_results"]["modelling_time"] / 60, 2),
        )
        return
