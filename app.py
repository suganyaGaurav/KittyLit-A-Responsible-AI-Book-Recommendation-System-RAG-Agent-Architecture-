"""
app.py
------
Entrypoint to run the Flask app. Uses create_app() factory.

Run:
$ python app.py
"""

from app import create_app
from app.config import FLASK_DEBUG

app = create_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0 so Docker demos can access the service.
    app.run(host="0.0.0.0", port=5000, debug=FLASK_DEBUG)
