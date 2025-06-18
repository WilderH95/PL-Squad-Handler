import requests
from bs4 import BeautifulSoup

def smart_capitalize(text):
    return ' '.join(word[0].upper() + word[1:] if word else '' for word in text.split())

request = requests.get("https://www.premierleague.com/clubs/10/Liverpool/squad?se=777")

soup = BeautifulSoup(request.text, features="html.parser")

#Get Opta IDs from the HTML
player_img_tag = soup.find_all(name='img', class_='statCardImg statCardPlayer')
photo_ids =[player_img_tag[n]['data-player'] for n in range(len(player_img_tag))]
print(photo_ids)

#Create a list of Opta IDs by stripping the "p" out of the Photo IDs
opta_ids = [n.strip("p") for n in photo_ids]
print(opta_ids)

#Get squad numbers from the HTML
squad_number_div = soup.find_all(name="div", class_='stats-card__squad-number u-hide-mob-l')
squad_numbers = [n.get_text() for n in squad_number_div]
print(squad_numbers)

#Get the first names from the HTML
first_name_div = soup.find_all(name="div", class_='stats-card__player-first')
first_names = [n.get_text() for n in first_name_div]
print(first_names)

#Get the last names from the HTML
last_name_div = soup.find_all(name="div", class_='stats-card__player-last')
last_names = [n.get_text() for n in last_name_div]
#Ensure all last names start with a capital letter
last_names = [smart_capitalize(n) for n in last_names]
print(last_names)
