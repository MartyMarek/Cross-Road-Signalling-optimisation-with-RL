import pandas as pd


class DataStore:

    # static class variable
    output_df = pd.DataFrame(
        columns=['step',
                    'ew_approaching', 'ew_stopped', 'ew_avrspeed', 'ew_waiting', 'ew_newthrough',
                    'ns_approaching', 'ns_stopped', 'ns_avrspeed', 'ns_waiting', 'ns_newthrough',
                    'sn_approaching', 'sn_stopped', 'sn_avrspeed', 'sn_waiting', 'sn_newthrough',
                    'we_approaching', 'we_stopped', 'we_avrspeed', 'we_waiting', 'we_newthrough'
                ]
    )

    def addNewRecord(self, record):
        df_length = len(self.output_df)
        self.output_df.loc[df_length] = record

    def _clearData(self):
        self.output_df.iloc[0:0]

    def saveCurrentRecord(self):
        print("saving observation file..")
        self.output_df.to_csv('observations.csv', index=False)
        self._clearData()
