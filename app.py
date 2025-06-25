from flask import Flask, render_template, request, redirect, url_for
from main import *
from dictionaries import *

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team = request.form.get('team')
        pl_data = get_pl_squad(team)
        current_sheet = read_sheet(team)
        merged_df = combine_df(current_sheet, pl_data)
        success, message = update_sheet(dataframe=merged_df, start_range='A6', team_name=team)
        return render_template('index.html', squad_urls=squad_urls, message=message)

    return render_template('index.html', squad_urls=squad_urls)

@app.route('/build', methods=['GET', 'POST'])
def build():
    if request.method == 'POST':
        team = request.form.get('team')
        pl_data = get_pl_squad(team)
        success, message = update_sheet(dataframe=pl_data, start_range='A6', team_name=team)
        return render_template('build.html', squad_urls=squad_urls, message=message)

    return render_template('build.html', squad_urls=squad_urls)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app.run(debug=True)