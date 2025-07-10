from flask import Flask, render_template, request, redirect, url_for
from dictionaries import *
from datahandler import DataHandler
import datetime
import os
from dotenv import load_dotenv


GOOGLE_API_KEY = "mads-database-463316-6011abf590bd.json"

load_dotenv()
OPTA_USER = os.getenv("OPTA_USER")
OPTA_KEY = os.getenv("OPTA_KEY")

app = Flask(__name__)

datahandler = DataHandler(google_api_key=GOOGLE_API_KEY, opta_user=OPTA_USER, opta_key=OPTA_KEY, season=8)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team = request.form.get('team')
        if team == "-":
            message = "Please select a valid option"
            return render_template('index.html', message=message, squad_urls=squad_urls, new_players = "-")
        else:
            pl_data = datahandler.get_pl_squad(team)
            current_sheet = datahandler.read_sheet(team)
            merged_df = datahandler.combine_df(current_sheet, pl_data)
            success, message = datahandler.update_sheet(dataframe=merged_df, start_range='A6', team_name=team)
            new_ps = datahandler.calculate_new_players(current_sheet, pl_data)
            now = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
            datahandler.populate_time(now, team)
            return render_template('index.html', squad_urls=squad_urls, message=message,
                                   new_players = new_ps, time=now)

    return render_template('index.html', squad_urls=squad_urls)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
