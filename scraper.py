# ====================================================
# TASK 4: Web Scraping and Data Extraction Pipeline
# Website: http://books.toscrape.com
# ====================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

BASE_URL = "http://books.toscrape.com/"
PAGE_URL = BASE_URL + "catalogue/page-{}.html"

# Create images folder
if not os.path.exists("images"):
    os.makedirs("images")

products = []

# =============================
# 1️⃣ Web Scraping with Pagination
# =============================

for page in range(1, 6):  # Scrape first 5 pages
    print(f"Scraping page {page}...")
    response = requests.get(PAGE_URL.format(page))
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    for book in books:
        name = book.h3.a["title"]
        price = book.find("p", class_="price_color").text.strip()

        rating_class = book.find("p", class_="star-rating")["class"][1]
        rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
        rating = rating_map.get(rating_class, 0)

        # Product page link
        product_link = BASE_URL + "catalogue/" + book.h3.a["href"].replace("../../../", "")
        product_response = requests.get(product_link)
        product_soup = BeautifulSoup(product_response.text, "html.parser")

        # Description
        description_tag = product_soup.find("div", id="product_description")
        if description_tag:
            description = description_tag.find_next_sibling("p").text.strip()
        else:
            description = "No description available"

        # Image URL
        image_relative = product_soup.find("img")["src"]
        image_url = BASE_URL + image_relative.replace("../../", "")

        # Download image
        image_data = requests.get(image_url).content
        image_filename = "images/" + re.sub(r'[^\w\s-]', '', name)[:40] + ".jpg"
        with open(image_filename, "wb") as f:
            f.write(image_data)

        products.append({
            "Product Name": name,
            "Price (£)": price,
            "Rating": rating,
            "Description": description,
            "Image URL": image_url
        })

# =============================
# 2️⃣ Data Cleaning
# =============================

df = pd.DataFrame(products)

df.drop_duplicates(inplace=True)

df["Price (£)"] = df["Price (£)"].str.replace("£","")
df["Price (£)"] = df["Price (£)"].astype(float)

df["Description"] = df["Description"].str.strip()

# =============================
# 3️⃣ Save CSV
# =============================

df.to_csv("products.csv", index=False)
print("CSV Saved!")

# =============================
# 4️⃣ Create HTML Dashboard
# =============================

total_products = len(df)
avg_price = round(df["Price (£)"].mean(),2)
avg_rating = round(df["Rating"].mean(),2)

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Product Dashboard</title>
<style>
body {{ font-family: Arial; padding:20px; }}
h1 {{ color:#2c3e50; }}
.card {{ background:#f4f4f4; padding:15px; margin:10px 0; }}
table {{ border-collapse: collapse; width:100%; }}
th, td {{ border:1px solid #ddd; padding:8px; }}
th {{ background:#3498db; color:white; }}
</style>
</head>
<body>

<h1>Web Scraping Summary Dashboard</h1>

<div class="card">
<p><strong>Total Products:</strong> {total_products}</p>
<p><strong>Average Price:</strong> £{avg_price}</p>
<p><strong>Average Rating:</strong> {avg_rating} / 5</p>
<p><strong>Minimum Price:</strong> £{df["Price (£)"].min()}</p>
<p><strong>Maximum Price:</strong> £{df["Price (£)"].max()}</p>
</div>

<h2>Sample Products</h2>
{df.head(5).to_html(index=False)}

</body>
</html>
"""

with open("dashboard.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard Created!")
print("Task Completed Successfully!")
