from flask import Flask, render_template, request

from pg_vis import keyword_names, background_colors, colors, get_landscape_assets, flatten

app = Flask(__name__)



# Sample tile data
tiles = flatten(get_landscape_assets())

@app.route("/")
def index():
    return render_template("index.html", tiles=tiles, keywords=keyword_names, colors=background_colors)

if __name__ == "__main__":
    app.run(debug=True)
