from stemmed import categorise_task

from flask import Flask, request

BASEPATH = "/recommender/v1"

app = Flask(__name__)


# TEST ENDPOINTS
@app.route(BASEPATH + "/")
def hello_world():
    return "Hello, World!"


@app.route(BASEPATH + "/test")
def hello_world2():
    return "Hello, World2!"


@app.route(BASEPATH + "/categorise-task")
def handle_categorise_task():
    data = request.get_json()
    name = data.get("name")
    desc = data.get("description")

    categorised_task = categorise_task(name, desc)
    return {"received": categorised_task}


# ACTUAL ENDPOINTS

if __name__ == "__main__":
    app.run(debug=True)
