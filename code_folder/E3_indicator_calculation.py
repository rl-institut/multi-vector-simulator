class indicators:
    def all_totals(dict_values):
        for column in dict_values["kpi"]["cost_matrix"].columns:
            dict_values["kpi"]["scalars"].update(
                {column: dict_values["kpi"]["cost_matrix"][column].sum()}
            )
        return
