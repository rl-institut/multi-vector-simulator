import pandas as pd


def randomize_shore_power(index, shore_power, filename=None, docks=1):
    # fuer docstring
    # Annahme bzw. Anforderung Daten:
    # Spalten in shore_power fassen Andock-Zeiten von Schiffen zusammen, die nicht gleichzeitig laden können.
    # Schiffe der versch. Spalten können gleichzeitig geladne werdne, wenn mehr als ein Dock. `docks`=1, 2, 3
    # todo einführen: Laden zweier Schiffe soll mind. einmal überlappen FRAGE: heißt überlappen kompl. Dauer des einen Schiffes oder mind. ein Zeitschritt?
    total_shore_power = pd.Series([0 for i in range(0, len(index))], index=index)

    for column in shore_power.columns:
        correct_combination = False
        while correct_combination != True:
            print("Get shore power times for: ", column, " docking time")
            time_of_events = pd.Series(
                [shore_power[column]["Power"] for i in range(0, len(index))], index=index
            ).sample(
                n=shore_power[column]["Number"], replace=False  # number of events
            )
            correct_combination = True
            number = 0
            for i in time_of_events.index:
                if correct_combination == True:
                    # check if period i collides with one of the other periods
                    for j in time_of_events.index:
                        if i != j:
                            if j in pd.date_range(
                                    start=i,
                                    end=i
                                        + pd.DateOffset(
                                        hours=int(shore_power[column]["Duration"])),
                                    freq="h",
                            ):   # note: 1 h mehr, da Zeit zum an und abfahren nötig
                                correct_combination = False

                    if correct_combination == True:
                        # write power to total_shore_power if there is an available
                        # dock and if time period does not exceed the date time
                        for hour in range(0, shore_power[column]["Duration"]):
                            try:
                                power = total_shore_power[
                                    i + pd.DateOffset(hours=hour)]
                            except KeyError:
                                # time period exceeds date time --> not possible
                                power = None
                            if power in [0, 500]: # todo  abh. v. docks
                                # dock is available
                                total_shore_power[
                                    i + pd.DateOffset(hours=hour)
                                ] += shore_power[column]["Power"]
                            else:
                                # dock not available or time period exceeds index
                                correct_combination = False
                                continue
                    else:
                        continue
                else:
                    continue

                if correct_combination == True:
                    number += 1
                    print(
                        "Valid random event ",
                        number,
                        " of total ",
                        shore_power[column]["Number"],
                    )
                else:
                    continue
    # todo add header to time series and maybe delete index
    total_shore_power.to_csv("demand_shore_power.csv")
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