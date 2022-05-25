import pandas as pd


class DataStore:

    # static class variable
    output_df = pd.DataFrame(
        columns=['step',
                    'en_approaching', 'en_stopped', 'en_avrspeed', 'en_waiting', 'en_newthrough',
                    'es_approaching', 'es_stopped', 'es_avrspeed', 'es_waiting', 'es_newthrough',
                    'ew_approaching', 'ew_stopped', 'ew_avrspeed', 'ew_waiting', 'ew_newthrough',
                    'ne_approaching', 'ne_stopped', 'ne_avrspeed', 'ne_waiting', 'ne_newthrough',
                    'ns_approaching', 'ns_stopped', 'ns_avrspeed', 'ns_waiting', 'ns_newthrough',
                    'nw_approaching', 'nw_stopped', 'nw_avrspeed', 'nw_waiting', 'nw_newthrough',
                    'se_approaching', 'se_stopped', 'se_avrspeed', 'se_waiting', 'se_newthrough',
                    'sn_approaching', 'sn_stopped', 'sn_avrspeed', 'sn_waiting', 'sn_newthrough',
                    'sw_approaching', 'sw_stopped', 'sw_avrspeed', 'sw_waiting', 'sw_newthrough',
                    'we_approaching', 'we_stopped', 'we_avrspeed', 'we_waiting', 'we_newthrough',
                    'wn_approaching', 'wn_stopped', 'wn_avrspeed', 'wn_waiting', 'wn_newthrough',
                    'ws_approaching', 'ws_stopped', 'ws_avrspeed', 'ws_waiting', 'ws_newthrough'
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
