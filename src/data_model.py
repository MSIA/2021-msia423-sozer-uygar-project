import logging

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

# Set up module logger
logger = logging.getLogger(__name__)

Base = declarative_base()


class Cuisine(Base):
    """Create a table for cuisines"""

    __tablename__ = 'cuisines'

    cuisineid = Column(Integer, primary_key=True)
    name = Column(String(20), unique=False, nullable=False)

    # String representation
    def __repr__(self):
        return '<Cuisine %r>' % self.title


class Ingredient(Base):
    """Create a table for ingredients"""

    __tablename__ = 'ingredients'

    ingredientid = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)

    # String representation
    def __repr__(self):
        return '<Ingredient %r>' % self.title


class Recipe(Base):
    """Create a table for recipes"""

    __tablename__ = 'recipes'

    recipeid = Column(Integer, primary_key=True)
    cuisineid = Column(ForeignKey("cuisines.cuisineid"),
                       unique=False,
                       nullable=False)

    # String representation
    def __repr__(self):
        return '<Recipe %r>' % self.title


class RecipeIngredient(Base):
    """Create a linking table for ingredients"""

    __tablename__ = 'recipe_ingredients'

    riid = Column(Integer, primary_key=True)

    # Create a relationship to autofill this table when
    # recipes/ingredients are added
    recipeid = Column(ForeignKey("recipes.recipeid"),
                      unique=False,
                      nullable=False)
    ingredientid = Column(ForeignKey("ingredients.ingredientid"),
                          unique=False,
                          nullable=False)

    # String representation
    def __repr__(self):
        return '<RecipeIngredient %r>' % self.title


def create_db(engine_string):
    """Create database from provided engine string
    Args:
        engine_string: str - Engine string for DB
    Returns: None
    """
    try:
        engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database created.")
    except sqlalchemy.exc.ArgumentError:
        logger.error("Invalid engine string provided")
    except sqlalchemy.exc.OperationalError:
        logger.error("Connection timed out, please check VPN connection")
    except Exception as e:
        logger.error("Unknown error", e)
