import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

conn_type = "mysql+pymysql"
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT")
database = os.environ.get("DATABASE_NAME")
engine_string = "{}://{}:{}@{}:{}/{}".format(conn_type, user, password, host, port, database)

Base = declarative_base()


class Cuisine(Base):
    """Create a data model for the database to be set up for capturing songs
    """

    __tablename__ = 'cuisines'

    cuisineid = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False, nullable=False)

    # def __repr__(self):
    #     return '<Track %r>' % self.title



class Ingredient(Base):
    """Create a data model for the database to be set up for capturing songs
    """

    __tablename__ = 'ingredients'

    ingredientid = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    
    # def __repr__(self):
    #     return '<Track %r>' % self.title


class Recipe(Base):
    """Create a data model for the database to be set up for capturing songs
    """

    __tablename__ = 'recipes'

    recipeid = Column(Integer, primary_key=True)
    cuisineid = Column(ForeignKey("cuisines.cuisineid"), unique=False, nullable=False)

    # def __repr__(self):
    #     return '<Track %r>' % self.title


class RecipeIngredient(Base):
    """Create a data model for the database to be set up for capturing songs
    """

    __tablename__ = 'recipe_ingredients'

    riid = Column(Integer, primary_key=True)
    recipeid = Column(ForeignKey("recipes.recipeid"), unique=False, nullable=False)
    ingredientid = Column(ForeignKey("ingredients.ingredientid"), unique=False, nullable=False)
    

    # def __repr__(self):
    #     return '<Track %r>' % self.title



def create_db():
    """Create database from provided engine string
    Args:
        engine_string: str - Engine string
    Returns: None
    """
    engine = sqlalchemy.create_engine(engine_string)

    Base.metadata.create_all(engine)
    #logger.info("Database created.")