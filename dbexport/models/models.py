import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from configdb.config_db import Session

# Create the Base class form where the table-classes will inherit
Base = declarative_base()

# Create the Session and the engine
session = Session()


class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    level = Column(Integer, nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    created_on = Column(TIMESTAMP)

    reviews = relationship("ReviewModel", order_by="ReviewModel.rating", back_populates="product")

    @classmethod
    def find_by_id(cls, _id):
        results = session.query(cls).filter_by(id=_id).first()
        return results

    @classmethod
    def find_published(cls):
        results = cls.query.filter_by(published=True).all()
        return list(results) if results else []

    @classmethod
    def get_products_with_reviews(cls):
        reviews_subquery = ReviewModel.get_reviews_per_product()
        products_query = (
            session.query(cls, reviews_subquery.c.reviews_count, reviews_subquery.c.ratings)
            .outerjoin(reviews_subquery, cls.id == reviews_subquery.c.product_id)
            .limit(30)
            .all()
        )
        return products_query

    def __str__(self):
        product = {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "published": self.published,
            "created_on": str(self.created_on),
        }
        return f"Product = {product}"

    def json(self):
        product = {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "published": self.published,
            "created_on": str(self.created_on),
        }
        return product


class ReviewModel(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(String(80))
    created_on = Column(TIMESTAMP, nullable=False, default=time.time())

    product = relationship("ProductModel", back_populates="reviews")

    @classmethod
    def get_reviews_per_product(cls):
        reviews_query = (
            session.query(
                cls.product_id.label("product_id"),
                func.count("*").label("reviews_count"),
                func.avg(cls.rating).label("ratings"),
            )
            .group_by(cls.product_id)
            .subquery()
        )

        return reviews_query
