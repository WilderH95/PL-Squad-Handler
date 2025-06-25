import pandas as pd
from dictionaries import *

class DFHandler:

    def __init__(self, opta_id, photo_id, squad_number, first_name, last_name):
        self.df = None
        self.data = {
            'Opta ID': [],
            'Photo Name': [],
            'Squad Number': [],
            'First Name': [],
            'Surname': []
        }
        for n in range(len(opta_id)):
            self.data['Opta ID'].append(opta_id[n])
            self.data['Photo Name'].append(photo_id[n])
            self.data['Squad Number'].append(squad_number[n])
            self.data['First Name'].append(first_name[n])
            self.data['Surname'].append(last_name[n])

    def create_df(self):
        self.df = pd.DataFrame(self.data)
        return self.df
