import os

DATABASE = {
    "HOST": os.getenv("DB_HOST", "localhost"),
    "USER": os.getenv("DB_USER","flask-db-user"),
    "PASSWORD": os.getenv("DB_PASS", "dunno"),
    "NAME": os.getenv("DB_NAME", "flask_test")
}
