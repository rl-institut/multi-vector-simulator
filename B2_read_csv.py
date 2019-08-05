'''
        # Copy input file to outputs
        for project_site in project_site_s:
            # copy input timeseries to new location
            path_from = os.path.abspath(settings['input_folder_timeseries'] + '/' + project_site_s[project_site]['timeseries_file'])
            path_to = os.path.abspath(settings['output_folder'] + '/inputs/'+ project_site_s[project_site]['timeseries_file'])
            shutil.copy(path_from, path_to)
'''

class csv_input():

    def column_not_existant(column_item, column_title, path_from):
        logging.error(
            'A column with the header "'+ column_title + '" as defined in the excel input file, tab "project sites", with "' + column_item + '" could not be found in '
            + '\n        ' + path_from
            + '\n        Check whether column exists, spelling is correct and for correct seperator of .csv file.')
        sys.exit(1) # Shutting down programm

    def from_file(project_site, path_from):
        ##########################################################
        # Reads timeseries from files connected to project sites #
        ##########################################################
        data_set = pd.read_csv(path_from, sep=project_site['seperator'])

        list_columns = ['title_time', 'title_demand_ac', 'title_demand_dc', 'title_pv', 'title_wind', 'title_grid_availability']

        # Attached data to each project site analysed. Does NOT apply noise here,
        # as noise might be subject to sensitivity analysis

        # Necessary: All of these input timeseries in same unit (kWh)

        # If-else clauses allow that some of the timeseries are not included in csv file.

        for column_item in list_columns:
            if column_item == 'title_time':
                if project_site[column_item] == 'None':
                    file_index = None
                else:
                    try:
                        file_index = pd.DatetimeIndex(data_set[project_site['title_time']].values)
                    except (KeyError):
                        csv_input.column_not_existant(column_item, project_site[column_item], path_from)
                project_site.update({'file_index': file_index})

            else:
                if column_item == 'title_demand_ac':
                    dictionary_title = 'demand_ac'
                elif column_item == 'title_demand_dc':
                    dictionary_title = 'demand_dc'
                elif column_item == 'title_pv':
                    dictionary_title = 'pv_generation_per_kWp'
                elif column_item == 'title_wind':
                    dictionary_title = 'wind_generation_per_kW'
                elif column_item == 'title_grid_availability':
                    dictionary_title = 'grid_availability'

                if project_site[column_item] != 'None':
                    try:
                        project_site.update({dictionary_title: data_set[project_site[column_item]]})
                    except (KeyError):
                        csv_input.column_not_existant(column_item, project_site[column_item], path_from)
                else:
                    if column_item != 'title_grid_availability':
                        if project_site[column_item] != 'None':
                            logging.warning('It is assumed that timeseries ' + column_item[6:] + ' is a vector of zeroes.')
                        project_site.update({dictionary_title: pd.Series([0 for i in range(0, 8760)])})

        return
