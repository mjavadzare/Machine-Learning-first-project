from bs4 import BeautifulSoup
import requests
import re
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
    host="Your HOST",
    user="root",
    password="Your Password",
    database="laptop",
)
cursor = dbc.cursor()

# Creating a table
cursor.execute(
    """
CREATE TABLE laptops(
    Name varchar(80),
    CPU varchar(50),
    RAM varchar(50),
    STORAGE varchar(50),
    VGA varchar(50),
    DISPLAY varchar(50),
    Price int,
    PRIMARY KEY (Name) )"""
)
dbc.commit()


Name_laptop = []

#  Fetching data from website and saving it into database
for page in range(1, 41):
    page = str(page)
    url = (
        "https://adak.shop/product-category/laptop-and-accessories/laptop/page/"
        + page
        + "/"
    )
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    twelve = soup.find_all("div", attrs={"class": "col-md-6 col-lg-6"})
    for laptop in twelve:
        name1 = laptop.find("div", attrs={"class", "ipba-content-heading"})
        name = name1.find("h3")
        Name = name.text
        if Name in Name_laptop:
            continue
        Name_laptop.append(Name)
        specs1 = laptop.find("div", attrs={"class", "ipba-content-list"})
        specs = specs1.find_all("li")
        price1 = laptop.find("span", attrs={"class": "woocommerce-Price-amount amount"})
        if re.match(r".*<bdi>(\d+,*\d*,*\d*)", str(price1)) is not None:
            Price = re.match(r".*<bdi>(\d+,*\d*,*\d*)", str(price1)).group(1)
            Price = Price.replace(",", "")
            Price = int(Price)
        else:
            continue
        CPU = re.match(r".+\s*:\s*(.*)<", str(specs[0])).group(1)
        RAM = re.match(r".+\s*:\s*(.*)<", str(specs[1])).group(1)
        STORAGE = re.match(r".+\s*:\s*(.*)<", str(specs[2])).group(1)
        VGA = re.match(r".+\s*:\s*(.*)<", str(specs[3])).group(1)
        DISPLAY = re.match(r"<li>Display\s*:*\s*(.*)<", str(specs[4])).group(1)

        cursor.execute(
            "INSERT INTO `laptops` VALUES( '%s', '%s', '%s', '%s' , '%s' , '%s' , '%i');"
            % (Name, CPU, RAM, STORAGE, VGA, DISPLAY, Price)
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
    x.append(row[1:6])
    y.append(row[6])

# Turning string data to encoded labels
clf = tree.DecisionTreeClassifier()
for i in range(len(x)):
    x[i] = le.fit_transform(x[i])
y = np.array(y)
clf = clf.fit(x, y)

# Your customized data and reshaping it:
test = np.array(
    ["Core i3 1215U", "16GB DDR4", "1TB SSD", "4GB GTX 1650", '15.6" FullHD 144Hz']
)
print(
    "Laptop with these specs:\nCPU: %s \nRAM: %s \nHardDisk: %s \nVGA: %s \nDisplay: %s \n"
    % (test[0], test[1], test[2], test[3], test[4])
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
