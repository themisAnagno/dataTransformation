import os
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@lru_cache(maxsize=32)
def engine_wrapper(db_url=None):
    """
    Wrappper for the SQLalchemy create_engine function. Uses the lru_cache decorator for returning
    always the same object (sqlalchemy engine) with the same input (db_url), storing it in cache
    """
    db_url = db_url or os.getenv("DB_URL")
    if not db_url:
        raise ValueError("database URL is required")
    return create_engine(db_url)


def get_connection(db_url=None):
    """
    Wrapper for the engine_wrapper function that takes the url and passes it to the other function.
    Returns it returns a connection of the created engine object
    """
    return engine_wrapper(db_url).connect()


@lru_cache(maxsize=32)
def sessionmaker_wrapper(db_url=None):
    """
    Calling the engine_wrappe, it creates the engine if it does not already exists
    Uses the lru_cache to cache the object and use it if the same url is passe
    """
    return sessionmaker(bind=engine_wrapper(db_url))


# Create the Session classs. This code will run when this module is imported.
# # Will only work with environment variable
try:
    Session = sessionmaker_wrapper()
except ValueError as e:
    print(e)
