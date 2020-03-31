import csv
from dbexport.config_db import Session
from models.models import ProductModel, ReviewModel
from sqlalchemy.sql import func

# Create the CSV writer object and the csv output file
csv_file = open("output.csv", mode="w")
fields = ["name", "level", "published", "created_on", "review_count", "avg_rating"]
csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
csv_writer.writeheader()

# Create the engine and the session objects
session = Session()

# Create a subquery from the reviews table that will be joint with a later query from the products
# table
reviews_subquery = (
    session.query(
        ReviewModel.product_id.label("product_id"),
        func.count("*").label("reviews_count"),
        func.avg(ReviewModel.rating).label("average_ratings"),
    )
    .group_by(ReviewModel.product_id)
    .subquery()
)

# Create the query to the products table
products_query = (
    session.query(
        ProductModel, reviews_subquery.c.reviews_count, reviews_subquery.c.average_ratings
    )
    .outerjoin(reviews_subquery, ProductModel.id == reviews_subquery.c.product_id)
    .all()
)

for product, review_count, ratings in products_query:
    dict = {
        "name": product.name,
        "level": product.level,
        "published": product.published,
        "created_on": str(product.created_on.date()),
        "review_count": review_count or 0,
        "avg_rating": round(float(ratings), 3) if ratings else 0,
    }
    csv_writer.writerow(dict)

print("Created the CSV file")
csv_file.close()
