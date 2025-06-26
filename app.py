from flask import Flask, render_template, request, redirect, url_for
from dictionaries import *
from datahandler import DataHandler

GOOGLE_API_KEY = "mads-database-463316-6011abf590bd.json"

app = Flask(__name__)

datahandler = DataHandler(GOOGLE_API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team = request.form.get('team')
        pl_data = datahandler.get_pl_squad(team)
        print(pl_data.shape)
        current_sheet = datahandler.read_sheet(team)
        print(current_sheet.shape)
        merged_df = datahandler.combine_df(current_sheet, pl_data)
        success, message = datahandler.update_sheet(dataframe=merged_df, start_range='A6', team_name=team)
        return render_template('index.html', squad_urls=squad_urls, message=message)

    return render_template('index.html', squad_urls=squad_urls)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app.run(debug=True)