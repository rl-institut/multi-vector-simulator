import pandas as pd

shore_power = {'Long': {'Number': 3, 'Duration': 400, 'Power': 500},
               'Short': {'Number': 20, 'Duration': 24, 'Power': 300}}
shore_power = pd.DataFrame(shore_power)
print(shore_power)

index = pd.date_range(start='1.1.2017 00:00', freq = 'h', periods = 8760)
total_shore_power = pd.Series ([0 for i in range(0, len(index))], index=index)

for column in shore_power.columns:
    correct_combination = False
    while correct_combination != True:
        print('Get shore power times for: ', column, ' docking time')
        time_of_events = pd.Series([shore_power[column]['Power'] for i in range(0, len(index))],
                                            index=index).sample(n=shore_power[column]['Number'], # number of events
                                                                    replace=False)
        correct_combination = True
        number = 0
        for i in time_of_events.index:
            for j in time_of_events.index:
                if i != j:
                    if j in pd.date_range(start=i, end=i + pd.DateOffset(hours=int(shore_power[column]['Duration'])), freq='h'):
                        correct_combination == False
                    else:
                        for hour in range(0,shore_power[column]['Duration']):
                            if total_shore_power[i + pd.DateOffset(hours=hour)] == 0:
                                total_shore_power[i + pd.DateOffset(hours=hour)]=shore_power[column]['Power']
                            else:
                                correct_combination == False

            number += 1
            print('Valid random event ', number, ' of total ', shore_power[column]['Number'])

total_shore_power.to_csv('shore_power_demand.csv')


