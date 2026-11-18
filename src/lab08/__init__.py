import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load variables from .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if not os.path.isfile(env_path):
            return False

        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                os.environ.setdefault(key, value)
        return True

load_dotenv()

app = Flask(__name__)

# Fetch the Neon URL from the environment (with a local fallback if needed)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

'''
# Define your routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
    '''