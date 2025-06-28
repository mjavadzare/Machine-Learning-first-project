from bs4 import BeautifulSoup
import requests
import mysql.connector
from sklearn import tree
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Creating a database if you haven't yet
# dbc = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     password = "admin",
#     )
# cursor = dbc.cursor()
# cursor.execute("CREATE DATABASE laptop")
# print("Database created successfully.")


# Connecting to database
dbc = mysql.connector.connect(
    host="localhost", user="root", password="Your Password", database="laptop"
)
cursor = dbc.cursor()

# Creating a table
# cursor.execute("""
# CREATE TABLE laptops (
#     Image LONGBLOB NULL,
#     Name VARCHAR(80),
#     CPU VARCHAR(50),
#     RAM VARCHAR(50),
#     DISPLAY VARCHAR(50),
#     VGA VARCHAR(50),
#     Price INT,
#     PRIMARY KEY (Name)
# )
# """)
# dbc.commit()
# print("Table created.")

Name_laptop = []

#  Fetching data from website and saving it into database
for page in range(1, 41):

    page = str(page)
    url = (
        "https://adak.shop/store/category/19322/%D9%84%D9%BE-%D8%AA%D8%A7%D9%BE?page="
        + page
    )
    res = requests.get(url).text
    print(res)
    soup = BeautifulSoup(res.text, "html.parser")
    sixteen = soup.find_all(
        "div", attrs={"class": "adak-product-card adak-product-card__category-list"}
    )

    for laptop in sixteen:
        for data in laptop:
            image_box = data.find("a", attrs={"class", "adak-product-card__img"})
            if image_box:
                img_tag = image_box.find("img")
                if img_tag and img_tag.has_attr("src"):
                    Image_url = img_tag["src"]
                else:
                    Image_url = None

            detail = data.find("div", attrs={"class", "product-detail"})
            title = detail.find("a", attrs={"class", "product-title"})

            # if title.hasattr("href"):
            #     laptop_url = title["href"]
            #     laptop_res = requests.get(url)
            #     laptop_soup = BeautifulSoup(laptop_res.text, "html.parser")
            #     more = laptop_soup.find_all(
            #         "div", attrs={"class", "product-info-features ng-star-inserted"}
            #     )
            #     feature_url = {}
            #     for feature in more:
            #         pass

            Name = title.text
            # Check whether data is duplicated
            if Name in Name_laptop:
                continue
            Name_laptop.append(Name)

            features = data.find_all("div", attrs={"class", "ng-star-inserted"})
            specs = []
            for feature in features:
                value_tag = feature.find("span", class_="product-feature-value")
                specs.append(value_tag)
            Cpu = specs[0].text
            Inch = specs[1].text
            Vga = specs[2].text
            Ram = specs[3].text

            # getting price
            price_box = data.find(
                "span", attrs={"class", "product-org-price text-left"}
            )
            price_box = price_box.find("div")
            price_box = price_box.find("span")
            Price = price_box.text
            Price = Price.replace(",", "")

            print(Price)
            print()
            cursor.execute(
                "INSERT INTO `laptops` VALUES( '%s', '%s', '%s', '%s' , '%s' , '%s' , '%i');"
                % (Image_url, Name, Cpu, Ram, Inch, Vga, Price)
            )
            dbc.commit()

"""
So far, we managed to fetch the data in order for printing.
Also we saved the data in Database and then...
"""

# Fetch data from database
all1 = "SELECT * FROM laptops"
cursor.execute(all1)
all = cursor.fetchall()

# Machine Learning Part:
x = []
y = []
le = LabelEncoder()
for row in all:
    x.append(row[2:6])
    y.append(row[6])

# Turning string data to encoded labels
clf = tree.DecisionTreeClassifier()
for i in range(len(x)):
    x[i] = le.fit_transform(x[i])
y = np.array(y)
clf = clf.fit(x, y)

# Your customized data and reshaping it:
test = np.array(
    [
        "Core i5",
        "16GB DDR4",
        "16.0",
        "UP TO 2GB",
    ]
)
print(
    "Laptop with these specs:\nCPU: %s \nRAM: %s \nDisplay: %s \nVGA: %s  \n"
    % (test[0], test[1], test[2], test[3])
)
new_data = le.fit_transform(test)
shape = new_data.reshape(1, -1)

"""
Now give me the knowledge of this computer for
predicting the price of my customized laptop!
"""

answer = int(clf.predict(shape))
print("Predicted Price: %i Toman" % answer)
cursor.close()
dbc.close()
