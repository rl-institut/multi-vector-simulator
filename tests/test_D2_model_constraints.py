import src.D2_model_constraints as D2

from src.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS

from src.constants_json_strings import (
    OEMOF_SOURCE,
    OEMOF_BUSSES,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_VECTOR,
    VALUE,
    LABEL,
    OUTPUT_BUS_NAME,
    DSO_CONSUMPTION,
    RENEWABLE_SHARE_DSO,
    RENEWABLE_ASSET_BOOL,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_SHARE,
)


def test_prepare_constraint_minimal_renewable_share():
    pv_plant = "PV"
    diesel = "Diesel"
    electricity = "Electricity"
    fuel = "Fuel"
    dso = "DSO"
    dict_values = {
        ENERGY_PROVIDERS: {dso: {LABEL: dso, RENEWABLE_SHARE_DSO: {VALUE: 0.3}}},
        ENERGY_PRODUCTION: {
            pv_plant: {
                RENEWABLE_ASSET_BOOL: {VALUE: True},
                LABEL: pv_plant,
                OUTPUT_BUS_NAME: electricity,
                ENERGY_VECTOR: electricity,
            },
            diesel: {
                RENEWABLE_ASSET_BOOL: {VALUE: False},
                LABEL: diesel,
                OUTPUT_BUS_NAME: fuel,
                ENERGY_VECTOR: electricity,
            },
            dso
            + DSO_CONSUMPTION: {
                LABEL: dso + DSO_CONSUMPTION,
                OUTPUT_BUS_NAME: electricity,
                ENERGY_VECTOR: electricity,
            },
        },
    }
    dict_model = {
        OEMOF_SOURCE: {
            pv_plant: pv_plant,
            diesel: diesel,
            dso + DSO_CONSUMPTION: dso + DSO_CONSUMPTION,
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

    assert pv_plant in renewable_assets
    assert pv_plant not in non_renewable_assets
    assert renewable_assets[pv_plant][renewable_share_asset_flow] == 1

    assert diesel in non_renewable_assets
    assert diesel not in renewable_assets
    assert non_renewable_assets[diesel][renewable_share_asset_flow] == 0

    assert dso + DSO_CONSUMPTION in renewable_assets
    assert renewable_assets[dso + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3

    assert dso + DSO_CONSUMPTION in non_renewable_assets
    assert (
        non_renewable_assets[dso + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3
    )
