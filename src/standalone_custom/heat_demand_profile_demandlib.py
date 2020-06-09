
        # sum in January - annual heat demand calc
        sum_jan = demand.iloc[0:24*31].sum()


        # calculate heat demand of only January:
        annual_demand_jan = 45630.42 * efficiency_gas_boiler  # kWh
        demand_jan = calculate_heat_demand_time_series(
            year=year,
            annual_demand=annual_demand_jan,
            ambient_temperature=weather["temp_air"].iloc[0:24*31],
            profile_type=profile_type,
            country=country,
            # filename=filename_heat_demand,
            frequency="H",
            hour_shift=hour_shift,
        )

        fig = plt.figure()
        demand_jan.plot()
        plt.xlabel("time")
        plt.ylabel("heat demand in kWh")
        # plt.show()
        # fig.savefig(os.path.join(folder, "heat_demand_year.pdf"))
        # only January
        plt.xlim([demand_jan.index[0], demand_jan.index[24 * 31 - 1]])
        fig.savefig(os.path.join(folder, "heat_demand_single_january.pdf"))

        # sum in January - only monthly calc
        sum_jan_single = demand_jan.sum()

        print(f"Demand January yearly calc: {round(sum_jan, 2)} kWh \nDemand January single calc: {round(sum_jan_single, 2)} kWh")

        print(f"January yearly calc: Min: {round(demand.min(), 2)} Max: {round(demand.max(), 2)} Diff: {round(demand.max()-demand.min(), 2)}\n"
              f"January monthly calc: Min: {round(demand_jan.min(), 2)} Max: {round(demand_jan.max(),2)} Diff: {round(demand_jan.max()-demand_jan.min(), 2)}")

        # check for July