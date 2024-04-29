import mariadb
import redis

from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = mariadb.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_DATABASE"]
        )
    return g.db

def get_redis():
    if "redis" not in g:
        g.redis = redis.StrictRedis(host="redis", port=6379, db=0)
    return g.redis

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def close_redis(e=None):
    redis = g.pop("redis", None)

    if redis is not None:
        redis.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_redis)