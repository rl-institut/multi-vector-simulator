import pandas as pd

def randomize_shore_power(index, shore_power, filename="demand_shore_power.csv", docks=1):
    # fuer docstring
    # Annahme bzw. Anforderung Daten:
    # Spalten in shore_power fassen Andock-Zeiten von Schiffen zusammen, die nicht gleichzeitig laden können.
    # Schiffe der versch. Spalten können gleichzeitig geladne werdne, wenn mehr als ein Dock. `docks`=1, 2, 3
    # todo einführen: Laden zweier Schiffe soll mind. einmal überlappen FRAGE: heißt überlappen kompl. Dauer des einen Schiffes oder mind. ein Zeitschritt?
    total_shore_power = pd.DataFrame([0 for i in range(0, len(index))], index=index, columns=['count'])

    for column in shore_power.columns:
        correct_combination = False
        while correct_combination != True:
            print("Get shore power times for: ", column, " docking time")  # todo logging
            time_of_events = pd.Series(
                [shore_power[column]["Power"] for i in range(0, len(index))], index=index
            ).reset_index()['index'].sample(
                n=shore_power[column]["Number"], replace=False  # number of events
            )
            correct_combination = True

            # check if any period collides with one of the other periods  # todo note: no time between charging
            # check, as well, whether periods stay within `times` # todo or index
            time_periods = time_of_events.apply(
                lambda x: pd.date_range(start=x, end=x + pd.DateOffset(
                    hours=int(shore_power[column]["Duration"] -1)),
                                        freq="h")).values
            joined_periods = time_periods[0]
            for i in range(1, len(time_periods)):
                joined_periods = joined_periods.join(time_periods[i],
                                                     how='outer')

            expected_length = (shore_power[column]["Duration"]) * len(
                time_of_events)
            if len(joined_periods) != expected_length or \
                    not index.contains(joined_periods[-1]):
                # try a new combination of "start" time steps
                correct_combination = False
                continue

            # write power to total_shore_power if there is an available dock #

            # check doc availability
            availability = total_shore_power['count'].loc[
                joined_periods].apply(lambda x: True if x < docks else False)
            if not availability.all():
                # try a new combination of "start" time steps
                correct_combination = False
                continue

            # temporary column
            total_shore_power[f'temp_{column}'] = 0
            total_shore_power.loc[joined_periods, f'temp_{column}'] = shore_power[column]['Power']

            # update count of docks
            total_shore_power.loc[joined_periods, 'count'] += 1

            # just to be sure: check whether expected sum was written
            expected_sum = (shore_power[column]['Power'] *
                            shore_power[column]['Duration'] *
                            shore_power[column]['Number'])
            if total_shore_power[f'temp_{column}'].sum() != expected_sum:
                # delete temporary column and try a new combination of "start"
                # time steps
                total_shore_power.drop(f'temp_{column}', axis=1, inplace=True)
                correct_combination = False
                continue

    # some information - to be extended if interesting
    max_docks_used = max(total_shore_power['count'])
    hours_without_docking = total_shore_power.loc[total_shore_power['count'] == 0.0].index
    amount_h_without_docking = len(hours_without_docking)

    # sum up shore power
    total_shore_power.drop('count', axis=1, inplace=True)
    total_shore_power = total_shore_power.sum(axis=1)

    # todo add header to time series and maybe delete index
    total_shore_power.to_csv(filename)
    return total_shore_power


if __name__ == "__main__":
    shore_power_df = {
        "Long": {"Number": 3, "Duration": 400, "Power": 500},
        "Short": {"Number": 20, "Duration": 24, "Power": 300},
    }
    shore_power_df = pd.DataFrame(shore_power_df)
    print(shore_power_df)
    times = pd.date_range(start="1.1.2017 00:00", freq="h", periods=8760)
    randomize_shore_power(index=times, shore_power=shore_power_df)