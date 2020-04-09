import pandas as pd
import matplotlib.pyplot as plt
import logging


logging.getLogger("matplotlib.font_manager").disabled = True


def flows(user_input, project_data, results_timeseries, sector, interval):
    """

    :param user_input:
    :param project_data:
    :param results_timeseries:
    :param sector:
    :param interval:
    :return:
    """
    logging.info("Creating plots for %s sector", sector)
    steps = interval * 24
    flows_les = results_timeseries[0:steps]

    includes_soc = False
    for column in results_timeseries.columns:
        if "SOC" in column:
            includes_soc = True
            soc_column_name = column

    if includes_soc == True:
        boolean_subplots = True
        flows_les = flows_les.drop([soc_column_name], axis=1)
    else:
        boolean_subplots = False

    if boolean_subplots == False:
        fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
        axes_mg = axes
    else:
        fig, axes = plt.subplots(nrows=2, figsize=(16 / 2.54, 10 / 2.54))
        axes_mg = axes[0]

    """
    # website with websafe hexacolours: https://www.colorhexa.com/web-safe-colors
    color_dict = {
        "total_demand_" + sector: "#33ff00",  # dark green
        "solar_inverter": "#ffcc00",  # orange
        #'Wind generation': '#33ccff',  # light blue
        #'Genset generation': '#000000',  # black
        "transformer_station_in": "#990099",  # violet
        "charge_controller_in": "#0033cc",  # light green
        sector + "_excess_sink": "#996600",  # brown
        "transformer_station_out": "#ff33cc",  # pink
        "charge_controller_out": "#ccccff",  # pidgeon blue
        #'Demand shortage': '#ff3300',  # bright red
        sector + "_storage_soc": "#0033cc"  # blue
        #'Grid availability': '#cc0000'  # red
    }
    """

    flows_les.plot(
        title=sector
        + " flows in Local Energy System: "
        + project_data["project_name"]
        + ", "
        + project_data["scenario_name"],
        # color=[color_dict.get(x, "#333333") for x in flows_les.columns],
        ax=axes_mg,
        drawstyle="steps-mid",
    )
    axes_mg.set(xlabel="Time", ylabel=sector + " flow in kWh")
    axes_mg.legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    if boolean_subplots == True:
        results_timeseries[soc_column_name][0:steps].plot(
            ax=axes[1],
            # color=color_dict.get(soc_column_name, "#333333"),
            drawstyle="steps-mid",
        )
        ylabel = sector + " SOC"

        axes[1].set(xlabel="Time", ylabel=ylabel)
        axes[1].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    plt.savefig(
        user_input["path_output_folder"]
        + "/"
        + sector
        + "_flows_"
        + str(interval)
        + "_days.png",
        bbox_inches="tight",
    )
    # plt.show()
    plt.close()
    plt.clf()
    plt.cla()

    return


def capacities(user_input, project_data, assets, capacities):
    """

    :param user_input:
    :param project_data:
    :param assets:
    :param capacities:
    :return:
    """

    # only items with an optimal added capacity over 0 are selected
    indexes = []
    capacities_added = []
    i = 0
    for capacity in capacities:
        if capacity > 0:
            indexes.append(i)
            capacities_added.append(capacity)
        i += 1
    i = 0
    assets_added = []
    for asset in assets:
        if i in indexes:
            assets_added.append(asset)
        i += 1

    # Data frame definition and plotting
    dfcapacities = pd.DataFrame()
    dfcapacities["items"] = assets_added
    dfcapacities["capacities"] = capacities_added

    logging.info("Creating bar-chart for components capacities")
    dfcapacities.plot.bar(
        x="items",
        y="capacities",
        title="Optimal additional capacities (kW/kWh/kWp): "
        + project_data["project_name"]
        + ", "
        + project_data["scenario_name"],
    )

    plt.savefig(
        user_input["path_output_folder"] + "/optimal_additional_capacities.png",
        bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()

    return


def costs(dict_values):
    """

    :param dict_values:
    :return:
    """

    settings = dict_values["simulation_settings"]
    project_data = dict_values["project_data"]

    # Annuity costs plot (only plot if there are values with cost over 0)
    label, path = "Annuities", "annuities_costs"
    show_annuity_total = False
    for element in dict_values["kpi"]["cost_matrix"]["annuity_total"].values:
        if element > 0:
            show_annuity_total = True
    if show_annuity_total:
        costs_total, total = plot_costs(
            settings,
            project_data,
            dict_values["kpi"]["cost_matrix"]["label"],
            dict_values["kpi"]["cost_matrix"]["annuity_total"],
            label,
            path,
        )

        # if there is a dominant assets, another plot with the remaining assets is created
        for asset in costs_total:
            if costs_total[asset] > 0.9 and costs_total[asset] < 1:
                major = asset
                major_value = costs_total[asset]
                plot_costs_rest(
                    settings,
                    project_data,
                    major,
                    major_value,
                    costs_total,
                    total,
                    label,
                    path,
                )

    # First-investment costs plot (only plot if there are values with cost over 0)
    label, path = "First-time investment", "first_time_investment_costs"
    show_costs_investment = False
    for element in dict_values["kpi"]["cost_matrix"]["costs_investment"].values:
        if element > 0:
            show_costs_investment = True
    if show_costs_investment:
        costs_total, total = plot_costs(
            settings,
            project_data,
            dict_values["kpi"]["cost_matrix"]["label"],
            dict_values["kpi"]["cost_matrix"]["costs_investment"],
            label,
            path,
        )

        # if there is a dominant assets, another plot with the remaining assets is created
        for asset in costs_total:
            if costs_total[asset] > 0.9 and costs_total[asset] < 1:
                major = asset
                major_value = costs_total[asset]
                plot_costs_rest(
                    settings,
                    project_data,
                    major,
                    major_value,
                    costs_total,
                    total,
                    label,
                    path,
                )

    # O&M costs plot (only plot if there are values with cost over 0)
    label, path = "Operation & Maintenance", "operation_and_maintenance_costs"
    show_costs_om = False
    for element in dict_values["kpi"]["cost_matrix"]["costs_om"].values:
        if element > 0:
            show_costs_om = True
    if show_costs_om:
        costs_total, total = plot_costs(
            settings,
            project_data,
            dict_values["kpi"]["cost_matrix"]["label"],
            dict_values["kpi"]["cost_matrix"]["costs_om"],
            label,
            path,
        )

        # if there is a dominant assets, another plot with the remaining assets is created
        for asset in costs_total:
            if costs_total[asset] > 0.9 and costs_total[asset] < 1:
                major = asset
                major_value = costs_total[asset]
                plot_costs_rest(
                    settings,
                    project_data,
                    major,
                    major_value,
                    costs_total,
                    total,
                    label,
                    path,
                )

    return


# costs are plotted in %
def plot_costs(settings, project_data, names, costs, label, path):
    """

    :param settings:
    :param project_data:
    :param names:
    :param costs:
    :param label:
    :param path:
    :return:
    """

    costs = pd.DataFrame(data=costs.values, index=names.values)
    costs = costs.to_dict()[0]

    # only assets with costs over 0 are plotted
    costs_prec = {}
    for asset in costs:
        if costs[asset] > 0:
            costs_prec.update({asset: costs[asset]})

    # % is calculated
    total = sum(costs_prec.values())
    costs_prec.update({n: costs_prec[n] / total for n in costs_prec.keys()})

    # those assets which do not reach 0,5% of total cost are included in 'others'
    # if there are more than one consumption period, they are grouped in DSO_consumption
    others = 0
    DSO_consumption = 0
    costs_total = {}
    for asset in costs_prec:
        if costs_prec[asset] > 0:
            if "DSO_consumption" in asset:
                DSO_consumption += costs_prec[asset]
            elif costs_prec[asset] < 0.005:
                others += costs_prec[asset]
            else:
                costs_total[asset] = costs_prec[asset]

    if DSO_consumption > 0:
        costs_total["DSO_consumption"] = DSO_consumption
    if others > 0:
        costs_total["others"] = others

    # dict is saved to proceed with plotting the remaining assets if there is a dominant one (more than 90%)
    costs_total_dict = costs_total

    costs_total = pd.Series(costs_total)
    logging.info("Creating pie-chart for total " + label)
    costs_total.plot.pie(
        title=label
        + " costs ("
        + str(round(total, 2))
        + "$): "
        + project_data["project_name"]
        + ", "
        + project_data["scenario_name"],
        autopct="%1.1f%%",
        subplots=True,
    )

    plt.savefig(
        settings["path_output_folder"] + "/" + path + ".png", bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()

    return costs_total_dict, total


# the rest of costs are plotted if there is a dominant one (over 90%)
def plot_costs_rest(
    settings, project_data, major, major_value, costs_total, total, label, path
):
    """

    :param settings:
    :param project_data:
    :param major:
    :param major_value:
    :param costs_total:
    :param total:
    :param label:
    :param path:
    :return:
    """

    costs_total_rest = costs_total.copy()
    del costs_total_rest[major]
    rest = sum(costs_total_rest.values())
    costs_total_rest.update(
        {n: costs_total_rest[n] / rest for n in costs_total_rest.keys()}
    )
    costs_total_rest = pd.Series(costs_total_rest)
    # check if there are any remaining costs that could be plotted
    if costs_total_rest.empty == False:
        costs_total_rest.plot.pie(
            title="Rest of "
            + label
            + "("
            + str(round((1 - major_value) * 100))
            + "% of "
            + str(round(total, 2))
            + "$): "
            + project_data["project_name"]
            + ", "
            + project_data["scenario_name"],
            autopct="%1.1f%%",
            subplots=True,
        )

        plt.savefig(
            settings["path_output_folder"] + "/" + path + "_other_costs.png",
            bbox_inches="tight",
        )

        plt.close()
        plt.clf()
        plt.cla()

    else:
        logging.debug(
            "No plot for costs_total_rest created, as remaining costs were 0."
        )
    return


def draw_graph(
    energysystem,
    user_input,
    edge_labels=True,
    node_color="#eeac7e",
    edge_color="#eeac7e",
    show_plot=True,
    save_plot=True,
    node_size=5500,
    with_labels=True,
    arrows=True,
    layout="dot",
):
    """

    :param energysystem:
    :param edge_labels:
    :param node_color:
    :param edge_color:
    :param plot:
    :param node_size:
    :param with_labels:
    :param arrows:
    :param layout:
    :return:
    """
    import networkx as nx
    import oemof.graph as graph

    grph = graph.create_nx_graph(energysystem)

    if type(node_color) is dict:
        node_color = [node_color.get(g, "#AFAFAF") for g in grph.nodes()]

    # set drawing options
    options = {
        "prog": "dot",
        "with_labels": with_labels,
        "node_color": node_color,
        "edge_color": edge_color,
        "node_size": node_size,
        "arrows": arrows,
        "font_size": 12,
        "font_color": "w",
    }

    # draw graph
    fig, ax = plt.subplots(figsize=(20, 10))
    pos = nx.drawing.nx_agraph.graphviz_layout(grph, prog=layout)

    nx.draw(grph, pos=pos, ax=ax, **options)

    # add edge labels for all edges
    if edge_labels is True and plt:
        labels = nx.get_edge_attributes(grph, "weight")
        nx.draw_networkx_edge_labels(grph, pos=pos, edge_labels=labels)

    if show_plot is True:
        fig.show()

    if save_plot:
        fig.savefig(
            user_input["path_output_folder"] + "/" + "network_graph.png",
            bbox_inches="tight",
        )
