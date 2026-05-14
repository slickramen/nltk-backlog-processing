from backlog_classifier import categorise_task
from flask import Flask, request, render_template, jsonify

BASEPATH = "/recommender/v1"

app = Flask(__name__)


# TEST ENDPOINTS
@app.route("/")
def home():
    return render_template("index.html", title="Welcome Page")


@app.route(BASEPATH + "/test")
def hello_world2():
    return "Hello, World2!"


def has_usable_categories(task):
    stack = (task.get("stack_layer") or "").strip().lower()
    implementations = [
        item
        for item in task.get("implementation_types") or []
        if item and item.strip().lower() != "unknown"
    ]
    concepts = [
        item
        for item in task.get("core_concepts") or []
        if item and item.strip().lower() != "unknown"
    ]

    return (
        stack in {"frontend", "backend", "fullstack"}
        or bool(implementations)
        or bool(concepts)
    )


@app.route(BASEPATH + "/categorise-task", methods=["POST"])
def handle_categorise_task():
    data = request.get_json() or {}
    title = data.get("title")
    desc = data.get("description") or ""

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        categorised_task = categorise_task(title, desc)
    except Exception as ex:
        app.logger.exception("Task classification failed")
        return jsonify(
            {
                "error": "task classification failed",
                "detail": str(ex),
            }
        ), 503

    if not has_usable_categories(categorised_task):
        return jsonify(
            {
                "error": "task classification produced no usable categories",
                "received": categorised_task,
            }
        ), 422

    return jsonify({"received": categorised_task})


# ACTUAL ENDPOINTS

if __name__ == "__main__":
    app.run(debug=True)
