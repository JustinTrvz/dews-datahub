from sqlalchemy import create_engine
from backend.config import DB_URL
from backend import app, db
import logging


class PSQLClient():
    url = DB_URL
    engine = None
    _connection = None
    session = None

    def __init__(self, session=None) -> None:
        if session is None:
            self.session = self.get_session()

    @classmethod
    def get_session(cls):
        with app.app_context():
            if cls.session is None:
                return db.session
            else:
                return cls.session

    @classmethod
    def close_session(cls):
        if cls.session is not None:
            cls.session.close()
            logging.debug(f"Closed database session. DB_URL='{DB_URL}'")
        return logging.info(f"No active database session. DB_URL='{DB_URL}'")

    @classmethod
    def init_db(cls):
        return_val = False
        try:
            import backend.database.models
            db.create_all()
            return_val = True
        except Exception as e:
            logging.error(
                f"Could not create database tables. DB_URL='{DB_URL}', Error='{e}'")

        cls.close_session()
        return return_val

    @classmethod
    def drop_db(cls):
        return_val = False
        try:
            import backend.database.models
            db.drop_all()
            return_val = True
        except Exception as e:
            logging.error(
                f"Could not drop database tables. DB_URL='{DB_URL}', Error='{e}'")

        cls.close_session()
        return return_val

    @classmethod
    def get_engine(cls):
        if cls.engine is None:
            try:
                return create_engine(DB_URL)
            except Exception as e:
                return logging.error(f"Could not create a database engine. DB_URL='{DB_URL}', Error='{e}'")
        else:
            return cls.engine

    @classmethod
    def connect(cls):
        """ Connect to the database server. """
        # global _connection

        if cls._connection is not None:
            return cls._connection

        try:
            # connect to PSQL server
            cls._connection = cls.engine.connect()
            return cls._connection
        except Exception as e:
            return logging.error(f"Connection to database failed. url='{cls.url}', error='{e}'")

    @staticmethod
    def close(cls):
        """ Closes connection to database server. """
        # global _connection

        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None
            logging.debug(
                f"Closed connection to the database server. url='{cls.url}'")
        else:
            logging.info(
                f"Did not disconnected the connection to the database server as there is no connection available. DB_URL='{DB_URL}'")

    @classmethod
    def create(cls, model, **kwargs):
        """
        Creates a database item from the passed model and adds it to the database.

        Returns a tuple with the id and the initialized object.

        Example: `(99, DbUser<'testuser'>)`

        If you only want the id or the object as return value, use the underscore syntax for the variable that you do not need.

        Example: `_, user = create(DbUser, ...)`.
        """
        logging.debug(
            f"Creating model '{model}' with keyword arguments '{kwargs}'")
        session = PSQLClient.get_session()

        try:
            result = model(**kwargs)
            id = result.id

            # Check if item exists in database
            logging.debug(
                f"Checking if item exists. url='{cls.url}', model='{model}', id='{id}'")
            existing_item = session.query(model).filter_by(id=id).first()

            if existing_item:
                # Item exists
                logging.debug(
                    f"Item already exists in database. url='{cls.url}', model='{model}', id='{id}'")
                return (existing_item.id, existing_item)
            else:
                # Item does not exist
                session.add(result)
                session.commit()
                logging.debug(
                    f"Added item to database. url='{cls.url}', model='{model}', id='{id}'")
                return (id, result)
        except Exception as e:
            logging.error(
                f"Failed to add item to database. url='{cls.url}', model='{model}', id='{id}', error='{e}'")
            return (None, None)

    @classmethod
    def read(cls, model, entry_id=None):
        """ 
        Reads and returns all entries or entry by id.

        Parameter `entry_id` is optional and if it is provided the entry matching this id will be returned. Otherwise all entries will be returned.
        """
        session = PSQLClient.get_session()

        try:
            if entry_id is None:
                # Read all entries
                result = session.query(model).all()
            else:
                # Read entry by id
                result = session.query(model).get(entry_id)
            return result
        except Exception as e:
            logging.error(
                f"Could not read from database. model='{model}', entry_id='{entry_id}', error='{e}'")
            return None

    @classmethod
    def update(cls, model, entry_id, **kwargs):
        session = PSQLClient.get_session()
        return_val = False

        try:
            result = session.query(model).get(entry_id)
            if result:
                for key, value in kwargs.items():
                    setattr(result, key, value)
                session.commit()
            return_val = True
        except Exception as e:
            logging.error(
                f"Could update entry in database. model='{model}', entry_id='{entry_id}', error='{e}'")

        cls.close_session()
        return return_val

    @classmethod
    def delete(cls, model, entry_id):
        session = PSQLClient.get_session()
        return_val = False

        try:
            result = session.query(model).get(entry_id)
            if result:
                session.delete(result)
                session.commit()
            return_val = True
        except Exception as e:
            logging.error(
                f"Could not delete entry in database. model='{model}', entry_id='{entry_id}', error='{e}'")

        cls.close_session()
        return return_val

    @classmethod
    def get_img_info(sd_id: str, img_type: str):
        """ Returns image path to the image which relates to the satellite data `sd_id` and has the image type `img_type`. """
        # Get image info from database
        from backend.database.models import ImageInfo
        try:
            img_info: ImageInfo = ImageInfo.query.filter(
            ImageInfo.sd_id == sd_id,
            ImageInfo.img_type == img_type
            ).first()
        except Exception as e:
            logging.error(f"Could not get image path from database. sd_id='{sd_id}', img_type='{img_type}', error='{e}'")
            return None

        # Return image info's image path
        return img_info

    @classmethod
    def get_sd(sd_id):
        # Get satellite data from database
        from backend.database.models import DbSatelliteData
        try:
            sd: DbSatelliteData = DbSatelliteData.query.filter(
            DbSatelliteData.id == sd_id
            ).first()
        except Exception as e:
            logging.error(f"Could not get satellite data from database. sd_id='{sd_id}', error='{e}'")
            return None

        # Return satellite data object
        return sd.test()