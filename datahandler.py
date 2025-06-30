import gspread
import pandas as pd
from gspread.utils import Dimension
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from dfhandler import DFHandler
from dictionaries import *
from pyuca import Collator

collator = Collator()

class DataHandler:

    def __init__(self, api_key):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(api_key, self.scope)
        self.client = gspread.authorize(self.creds)
        self.worksheet = None
        self.url = None
        self.request = None
        self.soup = None
        self.all_players = None
        self.photo_ids = None
        self.squad_numbers = None
        self.first_names = None
        self.last_names = None
        self.opta_ids = None
        self.site_dh = None
        self.site_df = None
        self.sorted_df = None
        self.current_sheet = None
        self.sh_opta_ids = None
        self.sh_photo_ids = None
        self.sh_squad_numbers = None
        self.sh_first_names = None
        self.sh_last_names = None
        self.sheet_dh = None
        self.sheet_df = None
        self.merged_df = None
        self.with_opta_id = None
        self.no_opta_id = None
        self.sort_by_no = None
        self.drop_dups = None
        self.recombined_df = None
        self.sorted_merged_df = None
        self.h_front = None
        self.h_celeb = None
        self.h_perso = None
        self.h_back = None
        self.a_front= None
        self.a_celeb = None
        self.a_perso = None
        self.a_back = None
        self.notes = None
        self.qc_coms = None
        self.new_players_list = []

    def _open_sheet(self, team_name):
        self.sheet = self.client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1RQxJpTLtRL7gnaQ0iACbdPKYkYXpm9rY1Od2vKE8bOM"
            "/edit?gid=977708243#gid=977708243")
        return self.sheet.worksheet(team_name)

    def update_sheet(self, dataframe, start_range, team_name):
        try:
            self.worksheet = self._open_sheet(team_name)
            self.worksheet.batch_clear(['A6:O59'])
            self.worksheet.update(range_name=start_range, values=dataframe.values.tolist())

            return True, f"{team_name} squad updated successfully"

        except Exception as e:
            return False, f"Failed to update {team_name}: {e}"

    def _smart_capitalise(self, text):
        return ' '.join(word[0].upper() + word[1:] if word else '' for word in text.split())

    def get_pl_squad(self, team_name):
        self.url = squad_urls[team_name]
        self.request = requests.get(self.url)
        self.soup = BeautifulSoup(self.request.text, features="html.parser")

        # Parse the HTML to grab all the player cards from the squad page
        self.all_players = self.soup.find_all('li', class_='stats-card')

        # Initialise lists
        self.photo_ids = []
        self.squad_numbers = []
        self.first_names = []
        self.last_names = []

        for player in self.all_players:
            # Get Opta IDs from the HTML
            photo_id = player.find(name='img', class_='statCardImg statCardPlayer')
            if photo_id:
                self.photo_ids.append(photo_id['data-player'])
            else:
                self.photo_ids.append(None)

            # Get squad numbers from the HTML
            squad_number = player.find(name="div", class_='stats-card__squad-number u-hide-mob-l')
            if squad_number:
                self.squad_numbers.append(squad_number.get_text())
            else:
                self.squad_numbers.append(None)

            # Get the first names from the HTML
            first_name = player.find(name="div", class_='stats-card__player-first')
            if first_name:
                self.first_names.append(first_name.get_text().strip())
            else:
                self.first_names.append(None)

            # Get the last names from the HTML
            last_name = player.find(name="div", class_='stats-card__player-last')
            if last_name:
                self.last_names.append(last_name.get_text().strip())
            else:
                self.last_names.append(None)

        # Create a list of Opta IDs by stripping the "p" out of the Photo IDs
        self.opta_ids = [n.strip("p") for n in self.photo_ids]

        # Ensure all last names start with a capital letter
        self.last_names = [self._smart_capitalise(n) for n in self.last_names]

        # Populate the data dict and create df. Output the df as a csv file
        self.site_dh = DFHandler()
        self.site_dh.populate_PL_data(self.opta_ids, self.photo_ids, self.squad_numbers,
                                                       self.first_names, self.last_names)
        self.site_df = self.site_dh.create_df()
        self.sorted_df = self.site_df.sort_values(
            by="Surname",
            key=lambda col: col.map(lambda x: collator.sort_key(x or ""))
        )

        self.sorted_df = self.sorted_df.fillna(" ")

        return self.sorted_df

    def read_sheet(self, team):
        self.worksheet = self._open_sheet(team)
        try:
            self.current_sheet = self.worksheet.get(range_name='A6:O59', major_dimension=Dimension.cols, pad_values=True)
            self.sh_opta_ids = self.current_sheet[0]
            self.sh_photo_ids = self.current_sheet[1]
            self.sh_squad_numbers = self.current_sheet[2]
            self.sh_first_names = self.current_sheet[3]
            self.sh_last_names = self.current_sheet[4]
            self.h_front = self.current_sheet[5]
            self.h_celeb = self.current_sheet[6]
            self.h_perso = self.current_sheet[7]
            self.h_back = self.current_sheet[8]
            self.a_front = self.current_sheet[9]
            self.a_celeb = self.current_sheet[10]
            self.a_perso = self.current_sheet[11]
            self.a_back = self.current_sheet[12]
            self.notes = self.current_sheet[13]
            self.qc_coms = self.current_sheet[14]
            self.sheet_dh = DFHandler()
            self.sheet_dh.populate_sheet_data(self.sh_opta_ids, self.sh_photo_ids, self.sh_squad_numbers,
                                              self.sh_first_names, self.sh_last_names, self.h_front, self.h_celeb,
                                              self.h_perso, self.h_back, self.a_front, self.a_celeb, self.a_perso,
                                              self.a_back, self.qc_coms, self.notes)

            self.sheet_df = self.sheet_dh.create_df()

            if self.sheet_df is not None and 'Surname' in self.sheet_df.columns:
                self.sheet_df = self.sheet_df[
                    self.sheet_df["Surname"].notna() & (self.sheet_df["Surname"].str.strip() != "")
                    ]
            else:
                self.sheet_df = pd.DataFrame()

            return self.sheet_df

        except IndexError:
            self.sh_opta_ids = []
            self.sh_photo_ids = []
            self.sh_squad_numbers = []
            self.sh_first_names = []
            self.sh_last_names = []
            self.sheet_dh = DFHandler()
            self.sheet_dh.populate_sheet_data(self.sh_opta_ids, self.sh_photo_ids, self.sh_squad_numbers,
                                              self.sh_first_names, self.sh_last_names, self.h_front, self.h_celeb,
                                              self.h_perso, self.h_back, self.a_front, self.a_celeb, self.a_perso,
                                              self.a_back, self.qc_coms, self.notes)
            self.sheet_df = self.sheet_dh.create_df()

            return self.sheet_df

    def combine_df(self, google_sheet, pl_data):
        # Combine the Google Sheet DF with the PL Website DF
        self.merged_df = pd.merge(google_sheet, pl_data, how="outer", on=["Opta ID", "Photo Name",
                                                                                          "Squad Number", "First Name",
                                                                                          "Surname"])
        # Separate the merged DF into one with all players with no Opta ID and ones with
        self.with_opta_id = self.merged_df[self.merged_df["Opta ID"].notna() & (self.merged_df["Opta ID"] != "")]
        self.no_opta_id = self.merged_df[self.merged_df["Opta ID"].isna() | (self.merged_df["Opta ID"] == "")]

        # Remove the duplicated players by Opta ID, ensuring those with a squad number remain if they exist
        self.sort_by_no = self.with_opta_id.sort_values('Squad Number', ascending=False)
        self.drop_dups = self.sort_by_no.drop_duplicates(subset="Opta ID")

        # Re-combine the Opta ID players and no Opta ID players
        self.recombined_df = pd.concat([self.drop_dups, self.no_opta_id], ignore_index=True)

        # Sort all the players by surname
        self.sorted_merged_df = self.recombined_df.sort_values(
            by="Surname",
            key=lambda col: col.map(lambda x: collator.sort_key(x or ""))
        ).reset_index(drop=True)

        self.sorted_merged_df = self.sorted_merged_df.fillna(" ")

        return self.sorted_merged_df

    def calculate_new_players(self, google_sheet, pl_data):
        # Compare the Google sheet and PL website data and create a new df containing only the new players from pl.com
        dup_players = pl_data[pl_data['Opta ID'].isin(google_sheet['Opta ID'])
                              & pl_data['Surname'].isin(google_sheet['Surname'])]

        new_players = pl_data[~pl_data['Opta ID'].isin(google_sheet['Opta ID'])
                              | ~pl_data['Surname'].isin(google_sheet['Surname'])]
        # Change the new players dataframe into a list for easy parsing in Jinja
        self.new_players_list = []
        for index, row in new_players.iterrows():
            self.new_players_list.append([row["Opta ID"], row["Squad Number"], row["First Name"], row["Surname"]])

        return self.new_players_list
