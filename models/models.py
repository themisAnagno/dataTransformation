import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

# Create the Base class form where the table-classes will inherit
Base = declarative_base()


class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    level = Column(Integer, nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    created_on = Column(TIMESTAMP, nullable=False, default=time.time())

    reviews = relationship("ReviewModel", order_by="ReviewModel.rating", back_populates="product")

    @classmethod
    def find_by_name(cls, name):
        results = cls.query.filter_by(name=name).first()
        return results

    @classmethod
    def find_published(cls):
        results = cls.query.filter_by(published=True).all()
        return list(results) if results else []

    def __str__(self):
        product = {"id": self.id,
                   "name": self.name,
                   "level": self.level,
                   "published": self.published,
                   "created_on": self.created_on}
        return f"Product = {product}"


class ReviewModel(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(String(80))
    created_on = Column(TIMESTAMP, nullable=False, default=time.time())

    product = relationship("ProductModel", back_populates="reviews")
