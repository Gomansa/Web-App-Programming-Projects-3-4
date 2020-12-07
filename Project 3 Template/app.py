from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField
import main_functions
import requests

creds = main_functions.read_from_file("creds.json")
password = creds["password"]

mongo_link = "mongodb+srv://Gomansa:{}@project3.x749h.mongodb.net/db?retryWrites=true&w=majority".format(password)

app = Flask(__name__)

app.config["SECRET_KEY"]="COP4813"
app.config["MONGO_URI"] = mongo_link

mongo = PyMongo(app)

class Expenses(FlaskForm):
    #You need to complete the foprm for the following fields:
    #StringField for description
    #SelectField for category
    #DecimalField for cost
    #DataField for date
    description = StringField('Description')
    category = SelectField('Category', choices=[('rent', 'Rent'),
                                                ('car', 'Car Payments'),
                                                ('food', 'Food'),
                                                ('credit', 'Credit')])

    cost = DecimalField('Cost')
    date = DateField('Date')

    currency = SelectField('Currency', choices=[('usd', 'USD'),
                                                ('canadian', 'Canadian Dollar'),
                                                ('euro', 'Euro'),
                                                ('gbp', 'Great British Pound')])

def currency_converter(cost, currency):

    url = "http://api.currencylayer.com/live?access_key=e5d4a53171bdfe2207dbbd82cfc70ab6&format=1"

    response = requests.get(url).json()

    if currency == 'usd':
        converted = cost
    elif currency == 'canadian':
        converted = cost / response["quotes"]["USDCAD"]
    elif currency == 'euro':
        converted = cost / response["quotes"]["USDEUR"]
    elif currency == 'gbp':
        converted = cost / response["quotes"]["USDGPB"]

    return converted


def get_total_expenses(category):
    #access the database adding the cost of all documents
    #of the category passed as input parameter
    #Write the appropriate query to retrieve the cost
    expense_category = 0
    query = {"category": category}
    records = mongo.db.expenses.find(query)

    for x in records:
        expense_category += float(x["cost"])
    return expense_category


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    expensesByCategory = [
        ("rent",get_total_expenses("rent")),
        ("car", get_total_expenses("car")),
        ("food", get_total_expenses("food")),
        ("credit", get_total_expenses("credit")),
    ]
    return render_template("index.html", expenses = total_cost, expensesByCategory=expensesByCategory)

@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    #INCLUDE THE FORM BASED ON CLASS EXPENSES
    expensesForm = Expenses(request.form)

    if request.method == "POST":
        #insert one document to the datavase
        #containing the data logged byt the user
        #rememver that it should be a python dictionary
        mongo.db.expenses.insert_one({
            "description": request.form['description'],
            "category": request.form['category'],
            "cost": float(request.form['cost']),
            "date": request.form['date'],
            "currency": request.form['currency'],

        })

        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form = expensesForm)

app.run()
