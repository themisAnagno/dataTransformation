import csv
from dbexport.config_db import Session
from models.models import ProductModel, ReviewModel
from sqlalchemy.sql import func

# Create the CSV writer object and the csv output file
csv_file = open("output.csv", mode="w")
fields = ["id", "name", "level", "published", "created_on", "review_count", "avg_rating"]
csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
csv_writer.writeheader()

products_query = ProductModel.get_products_with_reviews()
for product, review_count, ratings in products_query:
    data = product.json()
    data["review_count"] = review_count or 0
    data["avg_rating"] = round(float(ratings), 3) if ratings else 0

    csv_writer.writerow(data)

print("Created the CSV file")
csv_file.close()
