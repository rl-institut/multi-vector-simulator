import logging

class helpers():
    def check_optimize_cap(dict_asset, func_constant, func_optimize):
        if dict_asset['optimize_cap']==False:
            logging.info('Added to energy system model: Component %s, excluded from optimization.', dict_asset['label'])
            output = func_constant(dict_asset)
        elif dict_asset['optimize_cap']==True:
            logging.info('Added to energy system model: Component %s, to be optimized.', dict_asset['label'])
            output = func_optimize(dict_asset)
        else:
            logging.warning('Input error! '
                            '"optimize_cap" of asset %s not True/False.', dict_asset['label'])
        return output

class modelling_components():

    def genset_fix_efficiency(dict_asset):
        helpers.check_optimize_cap(dict_asset)

        def fix(dict_asset):
            return

        def optimize(dict_asset):
            return
        return

    def genset_var_efficiency(dict_asset):
        return

    # This could be used for wind plants and pv plants alike
    def source_non_dispatchable(dict_asset):
        return

    def shortage(dict_asset):
        return

    def sink_non_dispatchable(dict_asset):
        return


    def electricity_storage(dict_asset):
        return

    # Point of coupling of a single vector, eg. transformer station to external electricity grid
    def transformer_one_vector(dict_asset):
        return

    # Point of coupling of two energy vectors
    def transformer_two_vectors(dict_asset):
        return