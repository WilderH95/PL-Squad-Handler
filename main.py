import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from datahandler import DataHandler
from dictionaries import *

def smart_capitalize(text):
    return ' '.join(word[0].upper() + word[1:] if word else '' for word in text.split())

request = requests.get(squad_urls["Arsenal"])
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
dh = DataHandler(opta_ids, photo_ids, squad_numbers, first_names, last_names)
df = dh.create_df()
df.to_csv("out.csv", index=False, encoding='utf-8-sig')

# Google Sheets integration
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("mads-database-463316-736ad7930301.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1RQxJpTLtRL7gnaQ0iACbdPKYkYXpm9rY1Od2vKE8bOM"
                           "/edit?gid=977708243#gid=977708243")
worksheet = sheet.worksheet("Arsenal")
data = df.values.tolist()
worksheet.update(range_name='A6', values=data)