import logging

class economics:
    def get_costs(dict_asset, economic_data):
        if isinstance(dict_asset, dict) \
                and not(dict_asset['label'] in ['settings', 'economic_data', 'electricity_demand', 'simulation_settings', 'simulation_results']):
            logging.debug('Calculating costs of asset %s', dict_asset['label'])
            costs_total = 0
            cost_om = 0
            # Calculation of connected parameters:
            if helpers.all_list_in_dict(dict_asset, ['lifetime_capex_var', 'capex_fix', 'optimal_additional_capacity']) == True \
                    and dict_asset['optimal_additional_capacity'] > 0:
                # total investments including fix prices
                costs_investment = dict_asset['optimal_additional_capacity'] * dict_asset['lifetime_capex_var'] + dict_asset['capex_fix']
                costs_total = helpers.add_costs_and_total(dict_asset, 'costs_investment', costs_investment, costs_total)

            if helpers.all_list_in_dict(dict_asset, ['capex_var', 'capex_fix', 'optimal_additional_capacity']) == True \
                    and dict_asset['optimal_additional_capacity'] > 0:
                # investments including fix prices, only upfront costs at t=0
                costs_upfront = dict_asset['optimal_additional_capacity'] + dict_asset['capex_var'] + dict_asset['capex_fix']
                costs_total = helpers.add_costs_and_total(dict_asset, 'costs_upfront', costs_upfront, costs_total)

            if helpers.all_list_in_dict(dict_asset, ['annual_total_flow', 'lifetime_opex_var']) == True:
                costs_opex_var = dict_asset['lifetime_opex_var'] * dict_asset['annual_total_flow']
                costs_total = helpers.add_costs_and_total(dict_asset, 'costs_opex_var', costs_opex_var, costs_total)
                cost_om = helpers.add_costs_and_total(dict_asset, 'costs_opex_var', costs_opex_var, cost_om)

            if helpers.all_list_in_dict(dict_asset, ['price', 'annual_total_flow']) == True:
                costs_energy = dict_asset['price'] * dict_asset['annual_total_flow']
                cost_om = helpers.add_costs_and_total(dict_asset, 'costs_energy', costs_energy, cost_om)

            if helpers.all_list_in_dict(dict_asset, ['annual_total_flow', 'lifetime_opex_var', 'cap_installed', 'optimal_additional_capacity']) == True:
                cap = dict_asset['cap_installed']
                if 'optimal_additional_capacity' in dict_asset:
                    cap += dict_asset['optimal_additional_capacity']

                costs_opex_fix = dict_asset['lifetime_opex_fix']*cap
                costs_total = helpers.add_costs_and_total(dict_asset, 'costs_opex_fix', costs_opex_fix, costs_total)
                cost_om = helpers.add_costs_and_total(dict_asset, 'costs_opex_fix', costs_opex_fix, cost_om)

            dict_asset.update({'costs_total': costs_total,
                               'cost_om': cost_om})

            dict_asset.update({'annuity_total': dict_asset['costs_total'] * economic_data['crf'],
                               'annuity_om': dict_asset['cost_om'] * economic_data['crf']})
        return

class helpers:
    def add_costs_and_total(dict_asset, name, value, total_costs):
        total_costs += value
        dict_asset.update({name: value})
        return total_costs

    def all_list_in_dict(dict_asset, list):
        boolean = all([name in dict_asset for name in list]) == True
        return boolean