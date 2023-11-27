import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_mapping({
        "DB_HOST": os.environ.get("DB_HOST"),
        "DB_USER": os.environ.get("DB_USER"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD"),
        "DB_DATABASE": os.environ.get("DB_DATABASE")

    })
    from . import db
    db.init_app(app)

    from . import scores
    app.register_blueprint(scores.bp)

    return app