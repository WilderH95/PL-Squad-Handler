import requests
from bs4 import BeautifulSoup
from datahandler import DataHandler


def smart_capitalize(text):
    return ' '.join(word[0].upper() + word[1:] if word else '' for word in text.split())

request = requests.get("https://www.premierleague.com/clubs/131/Brighton-and-Hove-Albion/squad?se=777")

soup = BeautifulSoup(request.text, features="html.parser")

all_players = soup.find_all('li', class_='stats-card')

photo_ids = []
squad_numbers = []
first_names= []
last_names = []

for player in all_players:
    # #Get Opta IDs from the HTML
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

    # #Get the first names from the HTML
    first_name = player.find(name="div", class_='stats-card__player-first')
    if first_name:
        first_names.append(first_name.get_text().strip())
    else:
        first_names.append(None)

    last_name = player.find(name="div", class_='stats-card__player-last')
    if last_name:
        last_names.append(last_name.get_text().strip())
    else:
        last_names.append(None)

#Create a list of Opta IDs by stripping the "p" out of the Photo IDs
opta_ids = [n.strip("p") for n in photo_ids]

#Ensure all last names start with a capital letter
last_names = [smart_capitalize(n) for n in last_names]

# #Get the last names from the HTML
# last_name_div = soup.find_all(name="div", class_='stats-card__player-last')
# last_names = [n.get_text() for n in last_name_div]


dh = DataHandler(opta_ids, photo_ids, squad_numbers, first_names, last_names)
df = dh.create_df()
df.to_csv("out.csv", index=False, encoding='utf-8-sig')
