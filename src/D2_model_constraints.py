import pyomo.environ as po


def modelling_constraints():
    return


def standby_consumption(
    model, bus_electricity, bus_H2, electrolyser, standby_sink, efficiency
):
    """
    This function forces either the electrolyser or the strandy-by sink consumes 5% of
    the investment optimization of the electrolyser
    :param model:
    energy model
    :param bus_electricity:
    bus of electricity
    :param bus_H2:
    bus of H2
    :param electrolyser:
    electrolyser transformer
    :param standby_sink:
    sink for stand-by consumption. It only consumes when not the electrolyser is not producing H2
    :param efficiency:
    efficiency needed because the investment object is in the output, in the H2 bus. So we have to convert
    the investment value into electricity
    :return:
    """

    def standby_rule(model, t):
        minimum = 0.05 * model.InvestmentFlow.invest[electrolyser, bus_H2] / efficiency
        expr = -minimum
        expr += model.flow[bus_electricity, standby_sink, t]
        expr += model.flow[bus_electricity, electrolyser, t] / 10
        return expr >= 0

    model.stanby_consumption_constraint = po.Constraint(
        model.TIMESTEPS, rule=standby_rule
    )
    return model
