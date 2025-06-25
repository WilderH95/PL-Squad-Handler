import gspread
import pandas as pd
from gspread.utils import Dimension
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from dfhandler import DFHandler
from dictionaries import *
from pyuca import Collator

GOOGLE_API_KEY = "mads-database-463316-6011abf590bd.json"

collator = Collator()

def _open_sheet(team_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_KEY, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1RQxJpTLtRL7gnaQ0iACbdPKYkYXpm9rY1Od2vKE8bOM"
                               "/edit?gid=977708243#gid=977708243")
    return sheet.worksheet(team_name)

def update_sheet(dataframe, start_range, team_name):
    try:
        worksheet = _open_sheet(team_name)
        worksheet.batch_clear(['A6:E59'])
        worksheet.update(range_name=start_range, values=dataframe.values.tolist())

        return True, f"{team_name} squad updated successfully."

    except Exception as e:
        return False, f"Failed to update {team_name}: {e}"

def smart_capitalize(text):
    return ' '.join(word[0].upper() + word[1:] if word else '' for word in text.split())

def get_pl_squad(team_name):
    for key in data:
        data[key].clear()

    url = squad_urls[team_name]
    request = requests.get(url)
    soup = BeautifulSoup(request.text, features="html.parser")

    # Parse the HTML to grab all the player cards from the squad page
    all_players = soup.find_all('li', class_='stats-card')

    # Initialise lists
    photo_ids = []
    squad_numbers = []
    first_names= []
    last_names = []

    for player in all_players:
        # Get Opta IDs from the HTML
        photo_id = player.find(name='img', class_='statCardImg statCardPlayer')
        if photo_id:
            photo_ids.append(photo_id['data-player'])
        else:
            photo_ids.append(None)

        # Get squad numbers from the HTML
        squad_number = player.find(name="div", class_='stats-card__squad-number u-hide-mob-l')
        if squad_number:
            squad_numbers.append(squad_number.get_text())
        else:
            squad_numbers.append(None)

        # Get the first names from the HTML
        first_name = player.find(name="div", class_='stats-card__player-first')
        if first_name:
            first_names.append(first_name.get_text().strip())
        else:
            first_names.append(None)

        # Get the last names from the HTML
        last_name = player.find(name="div", class_='stats-card__player-last')
        if last_name:
            last_names.append(last_name.get_text().strip())
        else:
            last_names.append(None)

    # Create a list of Opta IDs by stripping the "p" out of the Photo IDs
    opta_ids = [n.strip("p") for n in photo_ids]

    # Ensure all last names start with a capital letter
    last_names = [smart_capitalize(n) for n in last_names]

    # Populate the data dict and create df. Output the df as a csv file
    site_dh = DFHandler(opta_ids, photo_ids, squad_numbers, first_names, last_names)
    site_df = site_dh.create_df()
    sorted_df = site_df.sort_values(
        by="Surname",
        key=lambda col: col.map(lambda x: collator.sort_key(x or ""))
    )
    return sorted_df

#TODO - Add error handling around reading an empty sheet.
def read_sheet(team_name):
    try:
        worksheet = _open_sheet(team_name)
        current_sheet = worksheet.get(range_name='A6:E59', major_dimension=Dimension.cols, pad_values=True)
        opta_ids = current_sheet[0]
        photo_ids = current_sheet[1]
        squad_numbers = current_sheet[2]
        first_names = current_sheet[3]
        last_names = current_sheet[4]
        sheet_dh = DFHandler(opta_ids, photo_ids, squad_numbers, first_names, last_names)
        sheet_df = sheet_dh.create_df()
        return sheet_df

    except IndexError:
        opta_ids = []
        photo_ids = []
        squad_numbers = []
        first_names = []
        last_names = []
        sheet_dh = DFHandler(opta_ids, photo_ids, squad_numbers, first_names, last_names)
        sheet_df = sheet_dh.create_df()
        return sheet_df


def combine_df(google_sheet, pl_data):
    merged_df = pd.merge(google_sheet, pl_data, how="outer", on=["Opta ID", "Photo Name", "Squad Number",
                                                                "First Name", "Surname"]
                         )

    sort_by_no = merged_df.sort_values('Squad Number', ascending=False)

    drop_dups = sort_by_no.drop_duplicates(subset="Opta ID")

    sorted_merged_df = drop_dups.sort_values(
        by="Surname",
        key=lambda col: col.map(lambda x: collator.sort_key(x or ""))
    )
    return sorted_merged_df