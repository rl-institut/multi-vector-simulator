import multi_vector_simulator.D2_model_constraints as D2

from multi_vector_simulator.utils.constants_json_strings import (
    OEMOF_SOURCE,
    OEMOF_BUSSES,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_VECTOR,
    VALUE,
    LABEL,
    OUTFLOW_DIRECTION,
    DSO_CONSUMPTION,
    RENEWABLE_SHARE_DSO,
    RENEWABLE_ASSET_BOOL,
)


def test_prepare_constraint_minimal_renewable_share():
    pv_plant = "PV"
    diesel = "Diesel"
    electricity = "Electricity"
    fuel = "Fuel"
    dso_1 = "DSO_1"
    dso_2 = "DSO_2"
    dict_values = {
        ENERGY_PROVIDERS: {
            dso_1: {LABEL: dso_1, RENEWABLE_SHARE_DSO: {VALUE: 0.3}},
            dso_2: {LABEL: dso_2, RENEWABLE_SHARE_DSO: {VALUE: 0.7}},
        },
        ENERGY_PRODUCTION: {
            pv_plant: {
                RENEWABLE_ASSET_BOOL: {VALUE: True},
                LABEL: pv_plant,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
            diesel: {
                RENEWABLE_ASSET_BOOL: {VALUE: False},
                LABEL: diesel,
                OUTFLOW_DIRECTION: fuel,
                ENERGY_VECTOR: electricity,
            },
            dso_1
            + DSO_CONSUMPTION: {
                LABEL: dso_1 + DSO_CONSUMPTION,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
            dso_2
            + DSO_CONSUMPTION: {
                LABEL: dso_2 + DSO_CONSUMPTION,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
        },
    }
    dict_model = {
        OEMOF_SOURCE: {
            pv_plant: pv_plant,
            diesel: diesel,
            dso_1 + DSO_CONSUMPTION: dso_1 + DSO_CONSUMPTION,
            dso_2 + DSO_CONSUMPTION: dso_2 + DSO_CONSUMPTION,
        },
        OEMOF_BUSSES: {electricity: electricity, fuel: fuel},
    }
    oemof_solph_object_asset = "object"
    weighting_factor_energy_carrier = "weighting_factor_energy_carrier"
    renewable_share_asset_flow = "renewable_share_asset_flow"
    oemof_solph_object_bus = "oemof_solph_object_bus"

    (
        renewable_assets,
        non_renewable_assets,
    ) = D2.prepare_constraint_minimal_renewable_share(
        dict_values=dict_values,
        dict_model=dict_model,
        oemof_solph_object_asset=oemof_solph_object_asset,
        weighting_factor_energy_carrier=weighting_factor_energy_carrier,
        renewable_share_asset_flow=renewable_share_asset_flow,
        oemof_solph_object_bus=oemof_solph_object_bus,
    )

    assert (
        pv_plant in renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        pv_plant not in non_renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        renewable_assets[pv_plant][renewable_share_asset_flow] == 1
    ), f"The renewable share of asset {pv_plant} is added incorrectly."

    assert (
        diesel in non_renewable_assets
    ), f"The {diesel} is added to the renewable assets."
    assert (
        diesel not in renewable_assets
    ), f"The {diesel} is not added to the non-renewable assets."
    assert (
        non_renewable_assets[diesel][renewable_share_asset_flow] == 0
    ), f"The renewable share of asset {diesel} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_1 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_1 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_2 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_2 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."
