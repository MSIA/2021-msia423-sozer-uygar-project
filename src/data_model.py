import logging

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Set up module logger
logger = logging.getLogger(__name__)

Base = declarative_base()

table_columns = [
    "name",
    "brazilian",
    "british",
    "cajun_creole",
    "chinese",
    "filipino",
    "french",
    "greek",
    "indian",
    "irish",
    "italian",
    "jamaican",
    "japanese",
    "korean",
    "mexican",
    "moroccan",
    "russian",
    "southern_us",
    "spanish",
    "thai",
    "vietnamese",
    "ingr_sum",
]


class Ingredient(Base):
    """Create a table for ingredients"""

    __tablename__ = "ingredients"

    cuisineid = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    brazilian = Column(Integer, unique=False, nullable=False)
    british = Column(Integer, unique=False, nullable=False)
    cajun_creole = Column(Integer, unique=False, nullable=False)
    chinese = Column(Integer, unique=False, nullable=False)
    filipino = Column(Integer, unique=False, nullable=False)
    french = Column(Integer, unique=False, nullable=False)
    greek = Column(Integer, unique=False, nullable=False)
    indian = Column(Integer, unique=False, nullable=False)
    irish = Column(Integer, unique=False, nullable=False)
    italian = Column(Integer, unique=False, nullable=False)
    jamaican = Column(Integer, unique=False, nullable=False)
    japanese = Column(Integer, unique=False, nullable=False)
    korean = Column(Integer, unique=False, nullable=False)
    mexican = Column(Integer, unique=False, nullable=False)
    moroccan = Column(Integer, unique=False, nullable=False)
    russian = Column(Integer, unique=False, nullable=False)
    southern_us = Column(Integer, unique=False, nullable=False)
    spanish = Column(Integer, unique=False, nullable=False)
    thai = Column(Integer, unique=False, nullable=False)
    vietnamese = Column(Integer, unique=False, nullable=False)
    ingr_sum = Column(Integer, unique=False, nullable=False)

    # String representation
    def __repr__(self):
        return "<Ingredients %r>" % self.title


def create_db(engine_string):
    """Create database from provided engine string

    Args:
        engine_string (str): Engine string for DB

    Returns:
        `sqlalchemy.orm.Session`: an `Engine` object
        to bind to session
    """
    try:
        engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database created.")

        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except sqlalchemy.exc.ArgumentError:
        logger.error("Invalid engine string provided")
    except sqlalchemy.exc.OperationalError:
        logger.error("Connection timed out, please check VPN connection")
    except Exception as e:
        logger.error("Unknown error", e)


def add_to_db(session, list_of_values):
    all_ingr = []
    for ingr_values in list_of_values:
        inserts = {
            table_columns[i]: ingr_values[i] for i in range(len(table_columns))
        }

        all_ingr.append(Ingredient(**inserts))

    session.add_all(all_ingr)
    session.commit()
