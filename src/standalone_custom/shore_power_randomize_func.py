import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)


def randomize_shore_power(times, shore_power,
                          filename="demand_shore_power.csv", docks=1):
    r"""
    Creates randomized shore power time series.

    times : pandas.DatetimeIndex
        Time period for which randomized shore power time series is created.
    shore_power : pandas.DataFrame
        Specification of shore power with row indices 'Duration' for the
        duration of a docking period of a ship, 'Number' showing the amount of
        docking events during `times` and 'Power` specifying the power of the
        respective ship. Add one column for each group of ships that share
        the same power and docking duration (name free to choose). It is
        assumed that ships of one column cannot occupy a dock at the same time,
        ships of different columns can though, if `docks` is greater than one.
    filename : str
        File name including path for saving the shore power time series.
        Default: "demand_shore_power.csv".
    docks : int
        Amount of docks that are available simultaneously. Default: 1.

    Returns
    -------
    total_shore_power : pandas.Series
        Randomized shore power time series.

    Todo
    -----
    * Adapt format of `total_shore_power` for MVS. (f.e. header, index ...)
    * Now there's now time step between two ships charging. There could be one
      one hour in between for docking and undocking.
    * Possible feature: Maximum amount of periods in which all docks are used.

    """
    total_shore_power = pd.DataFrame([0 for i in range(0, len(times))], index=times, columns=['count'])

    for column in shore_power.columns:
        correct_combination = False
        while correct_combination != True:
            logging.info(f"Get shore power times for ship type: {column}")
            # Get random time steps from time series
            time_of_events = pd.Series(
                [shore_power[column]["Power"] for i in range(0, len(times))], index=times
            ).reset_index()['index'].sample(
                n=shore_power[column]["Number"],  # number of events
                replace=False)
            correct_combination = True

            # check if any period collides with one of the other periods
            # check, as well, whether periods stay within `times`
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
            if (len(joined_periods) != expected_length or
                    not times.contains(joined_periods[-1])):
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

            # temporary column for charging power
            total_shore_power[f'temp_{column}'] = 0
            total_shore_power.loc[joined_periods, f'temp_{column}'] = shore_power[column]['Power']

            # update count of docks
            total_shore_power.loc[joined_periods, 'count'] += 1

            # just to be sure:
            # check whether expected sum was written to `total_shore_power`
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

    logging.info(f"Write shore power time series to file {filename}.")
    total_shore_power.to_csv(filename)
    return total_shore_power


if __name__ == "__main__":
    shore_power_df = {
        "Long": {"Number": 3, "Duration": 400, "Power": 500},
        "Short": {"Number": 20, "Duration": 24, "Power": 300},
    }
    shore_power_df = pd.DataFrame(shore_power_df)
    print(shore_power_df)
    time = pd.date_range(start="1.1.2017 00:00", freq="h", periods=8760)
    randomize_shore_power(times=time, shore_power=shore_power_df)