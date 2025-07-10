import gspread
import pandas as pd
from gspread.utils import Dimension
from oauth2client.service_account import ServiceAccountCredentials
import requests
from dfhandler import DFHandler
import dictionaries
from pyuca import Collator
import xml.etree.ElementTree as ET

collator = Collator()

class DataHandler:

    def __init__(self, google_api_key, opta_user, opta_key, season):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(google_api_key, self.scope)
        self.client = gspread.authorize(self.creds)
        self.worksheet = None
        self.url = (f"https://omo.akamai.opta.net/competition.php?user={opta_user}&psw={opta_key}&competition=8"
                    f"&season_id={season}&feed_type=F40")
        # self.url = "https://omo.akamai.opta.net/competition.php?user=AEL_BBCSport&psw=nm6YM5BDTE1PmPs&competition=8&season_id=2025&feed_type=F40"
        self.request = None
        self.soup = None
        self.all_players = None
        self.photo_ids = None
        self.squad_numbers = None
        self.first_names = None
        self.last_names = None
        self.opta_ids = None
        self.opta_dh = None
        self.opta_df = None
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

    def get_pl_squad(self, team):
        # Call opta squad list API and parse the text using xml.etree
        self.response = requests.get(self.url)
        root = ET.fromstring(self.response.text)
        # Find all teams present in the XML and store in variable
        clubs = root[0].findall('Team')
        # Get the selected team Opta ID from the 'teams' dictionary
        club_opta_id = dictionaries.teams[team]
        # Iterate through all teams in the XML and pick out the selected team
        selected_club = None
        for club in clubs:
            if club.attrib['uID'] == club_opta_id:
                selected_club = club

        # Get all the players from a selected team
        selected_players = selected_club.findall('Player')

        # Initialise lists
        self.photo_ids = []
        self.squad_numbers = []
        self.first_names = []
        self.last_names = []

        # Iterate over each player and pull out the required data
        for player in selected_players:
            photo_id = player.attrib['uID']
            if photo_id:
                self.photo_ids.append(photo_id)
            else:
                self.photo_ids.append(None)
            # Drill down into the stat for each player and pull out the text from those elements
            player_data = player.findall('Stat')
            for stat in player_data:
                stat_type = stat.get('Type')

                if stat_type == "jersey_num":
                    squad_number = stat.text
                    self.squad_numbers.append(squad_number)

                if stat_type == "first_name":
                    first_name = stat.text
                    self.first_names.append(first_name)

                if stat_type == "last_name":
                    last_name = stat.text
                    self.last_names.append(last_name)

        # If squad number is 'Unknown' replace with None
        self.squad_numbers = [unknown.replace('Unknown','') for unknown in self.squad_numbers]

        # Create a list of Opta IDs by stripping the "p" out of the Photo IDs
        self.opta_ids = [n.strip("p") for n in self.photo_ids]

        # Ensure all last names start with a capital letter
        self.last_names = [self._smart_capitalise(n) for n in self.last_names]

        # Populate the data dict and create df. Output the df as a csv file
        self.opta_dh = DFHandler()
        self.opta_dh.populate_PL_data(self.opta_ids, self.photo_ids, self.squad_numbers,
                                      self.first_names, self.last_names)
        self.opta_df = self.opta_dh.create_df()
        self.sorted_df = self.opta_df.sort_values(
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

    def populate_time(self, time, team_name):
        self.worksheet = self._open_sheet(team_name)
        self.worksheet.batch_clear(['C1:D1'])
        self.worksheet.update_acell('C2', time)