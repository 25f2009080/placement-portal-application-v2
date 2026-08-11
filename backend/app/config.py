import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "verysecret321"
    JWT_SECRET_KEY = "placement-portal-secret-key-2026-very-secure"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement_portal.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024     #5MB Limit

    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_REDIS_URL = "redis://127.0.0.1:6379/1"