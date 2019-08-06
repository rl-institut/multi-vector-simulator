from C1_verification import verify

class data_processing():
    def all(self):
        # Check, whether files (demand, generation) are existing
        verify.lookup_files()
        # Receive data from timeseries and process their format
        data_processing.timeseries()
        return

    # access recieve_data.timeseries_online and recieve_data.timeseries_csv indicidually
    def timeseries(self):
        return

class recieve_data:
    # read timeseries from file, adjust format, check for [0,1] in case of generation
    def timeseries_csv(self):
        return

    #get timeseries from online source
    def timeseries_online(self):
        return
