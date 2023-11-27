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

    app.config.from_envvar("DB_HOST")
    app.config.from_envvar("DB_USER")
    app.config.from_envvar("DB_PASSWORD")
    app.config.from_envvar("DB_DATABASE")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import scores
    app.register_blueprint(scores.bp)

    return app