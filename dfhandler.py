import pandas as pd
from dictionaries import *

class DataHandler:

    def __init__(self, opta_id, photo_id, squad_number, first_name, last_name):
        for n in range(len(opta_id)):
            data['Opta ID'].append(opta_id[n])
            data['Photo Name'].append(photo_id[n])
            data['Squad Number'].append(squad_number[n])
            data['First Name'].append(first_name[n])
            data['Surname'].append(last_name[n])

    def create_df(self):
        df = pd.DataFrame(data)
        return df
