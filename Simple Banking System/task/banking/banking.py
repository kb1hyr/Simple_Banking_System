# Write your code here
from os import path
import random
import sqlite3

logged_in = False
answer = 3
db_file = './card.s3db'
conn = None
cur = None


class CardRecord:
    db_id = ''
    db_number = ''
    db_pin = ''
    db_balance = ''

    def __init__(self):
        self.db_id = ''
        self.db_number = ''
        self.db_pin = ''
        self.db_balance = ''

    def save(self, id, number, pin, balance):
        self.db_id = id
        self.db_number = number
        self.db_pin = pin
        self.db_balance = balance

    def make_new(self):
        self.db_pin = self.make_pin()
        self.db_number = self.make_number()
        self.db_balance = 0

    def make_number(self):
        card_num = '400000'  # 6 digits
        for counter in range(9):
            card_num += str(random.randint(0, 9))
        card_num += self.create_check_digit(card_num)
        return card_num

    def make_pin(self):
        pin_str = ''
        for counter in range(4):
            pin_str += str(random.randint(0, 9))
        return pin_str

    def create_check_digit(self, cc_num):
        digits = list(map(int, cc_num + '0'))
        odd_sum = sum(digits[-1::-2])
        even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
        temp = (odd_sum + even_sum) % 10
        return str((10 - temp) % 10)

    def get_id(self):
        return self.db_id

    def get_pin(self):
        return self.db_pin

    def get_number(self):
        return self.db_number

    def get_balance(self):
        return self.db_balance

    def show_balance(self):
        print('')
        print('Balance: {}'.format(self.db_balance))

    def add_funds(self, amount):
        self.db_balance = self.db_balance + amount

    def remove_funds(self, amount):
        res = 0
        if self.db_balance - amount >= 0:
            self.db_balance = self.db_balance - amount
            res = 0
        else:
            res = 1  # error, can't decrease balance below zero
        return res

# Database routines for opening the database, adding, modifying and deleting entries


def db_open():
    global conn
    global cur
    global db_file
    if conn is None:
        if not path.isfile(db_file):
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE if not EXISTS card ('id' INTEGER, 'number' TEXT, 'pin' TEXT, balance INTEGER DEFAULT 0)")
            conn.commit()
        else:
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()


def db_save_new(card_record):
    global conn
    global cur
    db_open()
    query = "INSERT INTO card (pin, number, balance) VALUES(?,?,?)"
    cur.execute(query, (card_record.db_pin, card_record.db_number, card_record.db_balance))
    conn.commit()


def db_update_balance(card_record):
    global conn
    global cur
    query = "UPDATE card SET balance = ? WHERE number = ?"
    cur.execute(query, (card_record.db_balance, card_record.db_number))
    conn.commit()


def db_remove_record(card_record):
    global conn
    global cur
    query = "DELETE FROM card WHERE number = ?"
    cur.execute(query, (card_record.db_number,))
    conn.commit()


def db_get_card(number):
    this_card = CardRecord()
    success = False
    query = "SELECT id, number, pin, balance FROM card WHERE number = ?"
    for row in cur.execute(query, (number,)):
        success = True
        (this_card.db_id, this_card.db_number, this_card.db_pin, this_card.db_balance) = row
    if success:
        return this_card
    else:
        return None


# User functions
def check_luhn(cc_num):
    digits = list(map(int, cc_num))
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    result = (odd_sum + even_sum) % 10
    return result == 0


def menu():
    global logged_in
    if logged_in:
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')
    else:
        print('1. Create an account')
        print('2. Log into an account')
        print('0. Exit')
    return int(input())


def login_account():
    global logged_in
    global conn
    global cur
    balance = 0
    print('')
    print('Enter your card number:')
    card_num = input()
    print('Enter your PIN:')
    pin_num = input()

    success = False
    query = "SELECT balance FROM card WHERE number = ? AND pin = ?"
    for row in cur.execute(query, (card_num, pin_num)):
        success = True
        (row_data, *remaining) = row
        balance = int(row_data)

    if success:
        print('You have successfully logged in!')
        print('')
        logged_in = True
        my_card = db_get_card(card_num)
        return my_card
    else:
        print('Wrong card number or PIN!')
        print('')
        logged_in = False
        return None


def transfer():
    global the_card
    print('Transfer')
    print('Enter card number:')
    cc_num = input()
    if not check_luhn(cc_num):
        print('Probably you made a mistake in the card number. Please try again!')
        print('')
        return
    recipient = db_get_card(cc_num)
    if recipient == None:
        print('Such a card does not exist.')
        print('')
        return
    print('Enter how much money you want to transfer:')
    amount = int(input())
    if the_card.remove_funds(amount) == 1:
        print('Not enough money!')
        print('')
        return
    recipient.add_funds(amount)
    db_update_balance(the_card)
    db_update_balance(recipient)
    print('Success!')
    print('')


# Main program


# Connect to database
if not path.isfile(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("CREATE TABLE if not EXISTS card ('id' INTEGER, 'number' TEXT, 'pin' TEXT, balance INTEGER DEFAULT 0)")
    conn.commit()
else:
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

# Execute user choices
while answer != 0:
    answer = menu()
    if answer == 0:
        break

    if logged_in:
        if answer == 1:
            print(f"Balance: {the_card.get_balance()}")
            print('')
        if answer == 2:
            print('Enter income:')
            income = int(input())
            the_card.add_funds(income)
            db_update_balance(the_card)
            print('Income was added!')
            print('')
        if answer == 3:  # do transfer
            transfer()
        if answer == 4:  # close account
            db_remove_record(the_card)
            print('The account has been closed!')
            print('')
            logged_in = False
        if answer == 5:
            logged_in = False
            the_card = None
    else:
        if answer == 1:
            the_card = CardRecord()
            the_card.make_new()
            print('Your card has been created')
            print('Your card number:')
            print(the_card.db_number)
            print('Your card PIN:')
            print(the_card.db_pin)
            print('')
            db_save_new(the_card)
            the_card = None

        if answer == 2:
            the_card = login_account()

# Close database and leave
conn.close()
print('')
print('Bye!')

