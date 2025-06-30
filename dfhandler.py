import pandas as pd


class DFHandler:

    def __init__(self):
        self.df = None
        self.data = None

    def populate_PL_data(self, opta_id, photo_id, squad_number, first_name, last_name):
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

    def populate_sheet_data(self, opta_id, photo_id, squad_number, first_name, last_name, h_front, h_celeb, h_perso,
                            h_back, a_front, a_celeb, a_perso, a_back, notes, qc_coms):
        self.data = {
            'Opta ID': [],
            'Photo Name': [],
            'Squad Number': [],
            'First Name': [],
            'Surname': [],
            'Home Front': [],
            'Home Celeb': [],
            'Home Perso': [],
            'Home Back': [],
            'Away Front': [],
            'Away Celeb': [],
            'Away Perso': [],
            'Away Back': [],
            'Notes': [],
            'QC Comments': []
        }

        for n in range(len(last_name)):
            self.data['Opta ID'].append(opta_id[n])
            self.data['Photo Name'].append(photo_id[n])
            self.data['Squad Number'].append(squad_number[n])
            self.data['First Name'].append(first_name[n])
            self.data['Surname'].append(last_name[n])
            self.data['Home Front'].append(h_front[n])
            self.data['Home Celeb'].append(h_celeb[n])
            self.data['Home Perso'].append(h_perso[n])
            self.data['Home Back'].append(h_back[n])
            self.data['Away Front'].append(a_front[n])
            self.data['Away Celeb'].append(a_celeb[n])
            self.data['Away Perso'].append(a_perso[n])
            self.data['Away Back'].append(a_back[n])
            self.data['Notes'].append(notes[n])
            self.data['QC Comments'].append(qc_coms[n])

    def create_df(self):
        self.df = pd.DataFrame(self.data)
        return self.df
