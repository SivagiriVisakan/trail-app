import os

DATABASE = {
    "HOST": os.getenv("DB_HOST", "localhost"),
    "USER": os.getenv("DB_USER","flask-db-user"),
    "PASSWORD": os.getenv("DB_PASS", "dunno"),
    "NAME": os.getenv("DB_NAME", "flask_test")
}
SECRET_KEY=os.getenv("SECRET_KEY", None)

# It is set here for the time being, to take the load of our servers
TRAIL_JS_CLIENT_URL = "https://sivagirivisakan.github.io/trail-app/trail-client.js"