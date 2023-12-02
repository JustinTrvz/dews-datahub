from datetime import datetime
import uuid
from sqlalchemy import ForeignKey, Integer, Double, String, DateTime, Uuid, Column
from sqlalchemy.orm import relationship
from backend import db


class AreaInfo(db.Model):
    __tablename__ = "area_info"

    # Attributes
    id = Column(Integer, primary_key=True)
    area_name = Column(String(255))
    country = Column(String(255))
    city = Column(String(255))
    postal_code = Column(String(20))
    creation_time = Column(DateTime, default=datetime.utcnow)
    capture_time = Column(DateTime)

    # Foreign keys
    sd_id = Column(Uuid, ForeignKey("satellite_data.id"),
                   nullable=False)

    # References
    relationships = ["sd"]
    sd = relationship("DbSatelliteData",
                      back_populates="area_info")

    def to_dict(self):
        ModelUtil.to_dict(self)


class ImageInfo(db.Model):
    __tablename__ = "image_info"

    # Attributes
    id = Column(Integer, primary_key=True)
    img_type = Column(String(20))
    img_path = Column(String(255))
    # Assuming archived paths are stored as a JSON array
    archived_img_paths = Column(String)

    # Foreign keys
    sd_id = Column(Uuid, ForeignKey("satellite_data.id"),
                   nullable=False)

    # References
    relationships = ["sd"]
    sd = relationship("DbSatelliteData",
                      back_populates="image_info")

    def to_dict(self):
        ModelUtil.to_dict(self)


class BoundLatitudes(db.Model):
    __tablename__ = "bound_latitudes"

    # Attributes
    id = Column(Integer, primary_key=True)
    north = Column(Double)
    east = Column(Double)
    south = Column(Double)
    west = Column(Double)

    # Foreign keys
    sd_id = Column(Uuid, ForeignKey("satellite_data.id"),
                   nullable=False)

    # References
    relationships = ["sd"]
    sd = relationship("DbSatelliteData",
                      back_populates="bound_latitudes")

    def to_dict(self):
        ModelUtil.to_dict(self)


class CaptureInfo(db.Model):
    __tablename__ = "capture_info"

    # Attributes
    id = Column(Integer, primary_key=True)
    product_start_time = Column(DateTime)
    product_stop_time = Column(DateTime)
    product_type = Column(String(50))

    # Foreign keys
    sd_id = Column(Uuid, ForeignKey("satellite_data.id"),
                   nullable=False)

    # References
    relationships = ["sd"]
    sd = relationship("DbSatelliteData",
                      back_populates="capture_info")

    def to_dict(self):
        ModelUtil.to_dict(self)


class DbSatelliteData(db.Model):
    __tablename__ = "satellite_data"

    # Attributes
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    mission = Column(String(50))
    product_type = Column(String(50))
    directory_path = Column(String(255))
    manifest_path = Column(String(255))

    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"),
                     nullable=False)

    # References
    relationships = ["user", "calculations", "area_info",
                     "bound_latitudes", "capture_info", "image_info"]

    user = relationship("DbUser",
                        back_populates="sd_entries")
    calculations = relationship("DbCalculation",
                                back_populates="sd")

    area_info = relationship("AreaInfo",
                             back_populates="sd", uselist=False)
    bound_latitudes = relationship("BoundLatitudes",
                                   back_populates="sd", uselist=False)
    capture_info = relationship("CaptureInfo",
                                back_populates="sd", uselist=False)
    image_info = relationship("ImageInfo",
                              back_populates="sd")

    def to_dict(self):
        ModelUtil.to_dict(self)


# Relationship between DbUser and DbUserGroup
user_group_association = db.Table("user_group_association",
                                  Column("user_id", String,
                                         ForeignKey("users.id")),
                                  Column("group_id", String,
                                         ForeignKey("user_groups.id"))
                                  )


class DbUser(db.Model):
    __tablename__ = "users"

    # Attributes
    id = Column(String(50), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    mail = Column(String(50), nullable=False, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)

    # References
    relationships = ["groups", "sd_entries", "calculations"]

    groups = relationship("DbUserGroup",
                          secondary=user_group_association,
                          back_populates="users")
    sd_entries = relationship("DbSatelliteData",
                              back_populates="user", lazy=True)
    calculations = relationship("DbCalculation",
                                back_populates="user", lazy=True)

    def to_dict(self):
        ModelUtil.to_dict(self)


class DbUserGroup(db.Model):
    __tablename__ = "user_groups"

    # Attributes
    id = Column(String(50), primary_key=True)

    # References
    relationships = ["users"]
    users = relationship("DbUser", secondary=user_group_association,
                         back_populates="groups")

    def to_dict(self):
        ModelUtil.to_dict(self)


class DbCalculation(db.Model):
    __tablename__ = "calculations"

    # Attributes
    id = Column(Integer, primary_key=True)
    result = Column(String(50))

    # Foreign keys
    user_id = Column(String(50), ForeignKey("users.id"))
    sd_id = Column(Uuid, ForeignKey("satellite_data.id"))

    # References
    realtionships = ["user", "sd"]
    user = relationship("DbUser",
                        back_populates="calculations")
    sd = relationship("DbSatelliteData",
                      back_populates="calculations")

    def to_dict(self):
        ModelUtil.to_dict(self)


class ModelUtil():
    @staticmethod
    def to_dict(model):
        # Add attributes
        result = {column.name: getattr(model, column.name)
                  for column in model.__table__.columns}

        # Add items from realtionships/references
        if len(model.relationships) >= 1:
            for relationship_name in model.relationships:
                if hasattr(model, relationship_name):
                    result[relationship_name] = getattr(
                        model, relationship_name).to_dict()
