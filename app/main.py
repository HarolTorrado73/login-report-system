from flask import Flask, render_template

from app.report import events, generate_report

app = Flask(__name__)


@app.route("/")
def home():
    report = generate_report(events)

    return render_template(
        "index.html",
        report=report
    )


if __name__ == "__main__":
    app.run(debug=True)