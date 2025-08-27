from flask import Flask, render_template, request
from model import EbussRecommender

app = Flask(__name__)
svc = EbussRecommender()

@app.route("/", methods=["GET", "POST"])
def index():
    username = ""
    top5, top20 = [], []
    message = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        if not username:
            message = "Please enter a username."
        else:
            ids5 = svc.get_top5(username)
            ids20 = svc.get_top20(username)
            if not ids5 and not ids20:
                message = "Username not found. Try one of the examples below."
            else:
                top5 = [(pid, svc.product_name(pid)) for pid in ids5]
                top20 = [(pid, svc.product_name(pid)) for pid in ids20]

    examples = svc.available_users(limit=10)
    return render_template("index.html",
                           username=username,
                           top5=top5, top20=top20,
                           examples=examples)

if __name__ == "__main__":
    # local dev
    app.run(host="0.0.0.0", port=5000, debug=True)
