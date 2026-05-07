from stemmed import categorise_task

from flask import Flask, request, render_template

BASEPATH = "/recommender/v1"

app = Flask(__name__)


# TEST ENDPOINTS
@app.route("/")
def home():
    return render_template("index.html", title="Welcome Page")


@app.route(BASEPATH + "/test")
def hello_world2():
    return "Hello, World2!"


@app.route(BASEPATH + "/categorise-task", methods=["POST"])
def handle_categorise_task():
    data = request.get_json()
    title = data.get("title")
    desc = data.get("description")

    categorised_task = categorise_task(title, desc)
    return {"received": categorised_task}


# ACTUAL ENDPOINTS

if __name__ == "__main__":
    app.run(debug=True)
