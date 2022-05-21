import pandas as pd


class DataStore:

    # static class variable
    output_df = pd.DataFrame(
        columns=['step',
                    'ew_approaching', 'ns_approaching', 'sn_approaching', 'we_approaching',
                    'ew_stopped', 'ns_stopped', 'sn_stopped', 'we_stopped',
                    'ew_avrspeed', 'ns_avrspeed', 'sn_avrspeed', 'we_avrspeed',
                    'ew_waiting', 'ns_waiting', 'sn_waiting', 'we_waiting',
                    'ew_newthrough', 'ns_newthrough', 'sn_newthrough', 'we_newthrough'
                ]
    )

    def addNewRecord(self, record):
        df_length = len(self.output_df)
        self.output_df.loc[df_length] = record

    def _clearData(self):
        self.output_df.iloc[0:0]

    def saveCurrentRecord(self):
        self.output_df.to_csv(index=False)
        self._clearData()
