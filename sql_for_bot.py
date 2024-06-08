# sql-part of bot. insert and extract names of products, income and sums of it
# and second table - data of balance of bank acc and savings
# tables:
# Products - User, Date, Product, Price
# Balance - User, Date, Summary, Savings
# take input from bot, check that, take data from db tables
# calculate, insert new lines in tables

import sqlite3
import datetime


def new_db():
    # create tables Products and Balance if you need

    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS Products(
                Date TEXT,
                Product TEXT,
                Price REAL,
                User TEXT,
                );""")
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS Balance(
                Date TEXT,
                Summary REAL,
                Savings REAL,
                User TEXT,
                );""")


def take_bal_data(user):
    # take last record (Date, Summary, Savings) from Balance table

    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT Date, Summary, Savings FROM Balance WHERE User = ? ORDER BY date DESC LIMIT 1;",
                (user,))
            last_line = cursor.fetchone()
        except TypeError:
            return False
        except sqlite3.OperationalError:
            return False
        else:
            return last_line


def month_data(month, user):
    # take all records for month

    if month == 'this':
        this_month = str(datetime.date.today())[0:7]
        with sqlite3.connect('fin_table.db') as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT Date, Product, Price FROM Products WHERE Date LIKE ? AND User = ?;",
                    (this_month + "%", user))
                records = cursor.fetchall()
                if not records:
                    return False
            except TypeError:
                return False
            except sqlite3.OperationalError:
                return False
            else:  # give as last line sum of spendings
                cursor.execute(
                    "SELECT SUM(Price) FROM Products WHERE Date LIKE ? AND User = ? AND LOWER(Product)"
                    "NOT IN ('income', 'save', 'take');",
                    (this_month + "%", user))
                summary_of_month = (this_month,
                                    'Spendings',
                                    round(cursor.fetchone()[0], 2))
                records.append(summary_of_month)
    elif month == 'prev':
        prev_month = str()
        if datetime.datetime.today().month > 10:
            prev_month = f'{datetime.datetime.today().year}-{datetime.datetime.today().month - 1}'
        elif 10 >= datetime.datetime.today().month > 1:
            prev_month = f'{datetime.datetime.today().year}-0{datetime.datetime.today().month - 1}'
        elif datetime.datetime.today().month == 1:
            prev_month = f'{datetime.datetime.today().year - 1}-{12}'

        with sqlite3.connect('fin_table.db') as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT Date, Product, Price FROM Products WHERE Date LIKE ? AND User = ?;",
                    (prev_month + "%", user))
                records = cursor.fetchall()
                if not records:
                    return False
            except TypeError:
                return False
            except sqlite3.OperationalError:
                return False
            else:  # give as last line sum of spendings
                cursor.execute(
                    "SELECT SUM(Price) FROM Products WHERE Date LIKE ? AND User = ? AND LOWER(Product)"
                    "NOT IN ('income', 'save', 'take');",
                    (prev_month + "%", user))
                summary_of_month = (prev_month, 'Spendings', round(cursor.fetchone()[0], 2))
                records.append(summary_of_month)

    return records


def most_val_prev_month(user):
    prev_month = str()
    if datetime.datetime.today().month > 10:
        prev_month = f'{datetime.datetime.today().year}-{datetime.datetime.today().month - 1}'
    elif 10 >= datetime.datetime.today().month > 1:
        prev_month = f'{datetime.datetime.today().year}-0{datetime.datetime.today().month - 1}'
    elif datetime.datetime.today().month == 1:
        prev_month = f'{datetime.datetime.today().year - 1}-{12}'
    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                """SELECT Product, SUM(Price) AS Sum
                FROM Products WHERE Date LIKE ? AND User = ?
                AND LOWER(Product) NOT IN ('income', 'save', 'take')
                GROUP BY Product
                ORDER BY Sum DESC
                LIMIT 5;""",
                (prev_month + "%", user))
            records = cursor.fetchall()
            if not records:
                return False
        except TypeError:
            return False
        except sqlite3.OperationalError:
            return False

    return records


def calc_bal(product, cost, last_record):
    # if last record exists then take it and decrease with spendings
    # if product is income then increase
    # if save then increase savings and decrease summary
    # and if there's no records then just create it

    if last_record:
        summary, savings = last_record[1], last_record[2]
    else:
        summary = savings = 0

    if product.lower() == 'income':
        summary += abs(cost)
    elif product.lower() == 'save':
        summary -= abs(cost)
        savings += abs(cost)
    elif product.lower() == 'take':
        summary += abs(cost)
        savings -= abs(cost)
    else:
        summary -= abs(cost)

    return summary, savings


def check_date(user):
    # delete last line or record if date is today

    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM Balance WHERE Date = date('now', 'localtime') AND User = ?;",
            (user,))


def ins_prod_data(user, product, price):
    # inserting data to Products table

    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Products VALUES(date('now', 'localtime'), ?, ?, ?);",
            (product, price, user))


def ins_bal_data(user, summary, savings):
    # Insert data to Balance table

    with sqlite3.connect('fin_table.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Balance VALUES(date('now', 'localtime'), ?, ?, ?);",
            (summary, savings, user))
