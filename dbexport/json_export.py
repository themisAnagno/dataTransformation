import json
from dbexport.configdb.config_db import Session
from dbexport.models.models import ProductModel, ReviewModel
from sqlalchemy.sql import func


def run_export():
    items = []

    # Create the engine and the session objects
    session = Session()

    # Create a subquery from the reviews table that will be joint with a later query from the
    # products table
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
        .limit(30)
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
        items.append(dict)
    json_data = {"items": items}
    print("Created the JSON file")
    json.dumps(items)

    with open("output.json", mode="w") as f:
        json.dump(json_data, f)


if __name__ == "__main__":
    run_export()
