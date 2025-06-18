from flask import Flask, render_template, request, redirect, url_for
from scraper import update_squad
from dictionaries import *

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team = request.form.get('team')
        success, message = update_squad(team)
        return render_template('index.html', squad_urls=squad_urls, message=message)

    return render_template('index.html', squad_urls=squad_urls)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)