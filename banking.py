import random
import sqlite3

global client_status
client_status = 'logged_out'

# Creating the card database and the car table
global conn
conn = sqlite3.connect('card.s3db')
global cur
cur = conn.cursor()
cur.execute('DROP TABLE IF  EXISTS card;')
cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER default 0);')
conn.commit()


# Write your code here
class Account:
    def __init__(self):

        iin = 4000000000000000
        account_number = random.randrange(1, 10 ** 10)
        card_number = [e for e in str(iin + account_number)]
        # Luhn Algorithm step 1 : Remove the last digit from the card number
        card_number.pop()
        # Luhn Algorithm step 2 :Reverse the order of the remaining numbers
        card_number_reversed = [card_number[-i] for i in range(1, len(card_number) + 1)]
        processed_digits = []

        for index, digit in enumerate(card_number_reversed):
            if index % 2 == 0:
                doubled_digit = int(digit) * 2

                # Luhn Algorithm step 3 : Subtract 9 from any results that are greater than 9
                if doubled_digit > 9:
                    doubled_digit = doubled_digit - 9

                processed_digits.append(doubled_digit)
            else:
                processed_digits.append(int(digit))

        # Luhn Algorithm step 4 : find the checksum
        checksum = 10 - sum(processed_digits) % 10 if sum(processed_digits) % 10 != 0 else 0
        card_number.append(str(checksum))
        self.card_number = ''.join(card_number)
        self.pin_code = f'{random.randrange(1, 10 ** 4):04}'
        cur.execute(
            'INSERT INTO card (number, pin, balance) VALUES({}, {}, 0);'.format(self.card_number, self.pin_code))
        conn.commit()

    def print_recap(self):
        print('Your card has been created')
        print('Your card number:')
        print(self.card_number)
        print('Your card PIN:')
        print(self.pin_code)
        menu()


# Menu function: displaying options and allowing user to make choices
def menu():
    global active_session
    global client_status
    menu_logged_in = ['1. Balance', '2. Add income', '3. Do transfer', '4. Close account', '5. Log out', '0. Exit']
    menu_logged_out = ['1. Create an account', '2. Log into account', '0. Exit']
    if client_status == "logged_out":
        for e in menu_logged_out:
            print(e)
    elif client_status == 'logged_in':
        for e in menu_logged_in:
            print(e)

    if client_status == "logged_out":
        choice = input('')
        if choice == '1':
            a = Account()
            a.print_recap()
        elif choice == '2':
            log_in()
        elif choice == '0':
            exit_account()

    elif client_status == "logged_in":
        choice = input('')
        if choice == '1':
            balance(active_session)
        elif choice == '2':
            add_income(active_session)
        elif choice == '3':
            transfer(active_session)
        elif choice == '4':
            close_account(active_session)
        elif choice == '5':
            log_out()
        elif choice == '0':
            exit_account()


def balance(account):
    cur.execute('SELECT balance from card WHERE number = {};'.format(account))
    balance_account = cur.fetchone()[0]
    conn.commit()
    print('Balance: {}'.format(balance_account))
    menu()


def add_income(account):
    amount = int(input('Enter income:'))
    cur.execute('UPDATE card SET balance = balance + {} WHERE number = {};'.format(amount, account))
    conn.commit()
    print('Income was added!')
    menu()


def transfer(account):
    card_input = input('Enter card number:')
    if not is_luhn_valid(card_input):
        print('Probably you made a mistake in the card number. Please try again!')
        menu()
    elif not card_exists(card_input):
        print('Such a card does not exist.')
        menu()
    elif card_input == account:
        print("You can't transfer money to the same account!")
        menu()
    else:
        amount = int(input('Enter how much money you want to transfer:'))
        if not has_enough_money_account(account, amount):
            print('Not enough money!')
            menu()
        elif has_enough_money_account(account, amount):
            cur.execute('UPDATE card SET balance = balance + {} WHERE number = {};'.format(amount, card_input))
            cur.execute('UPDATE card SET balance = balance - {} WHERE number = {};'.format(amount, account))
            conn.commit()
            print('Success!')
            menu()


def close_account(account):
    cur.execute("DELETE  FROM card WHERE number = {}".format(account))
    conn.commit()
    menu()


def log_in():
    global active_session
    global client_status
    card_number_input = input('Enter your card number:')
    pin_code_input = input('Enter your PIN:')
    log_in.active_session = card_number_input

    if not is_pin_valid(pin_code_input) or not card_exists(card_number_input):
        print('Wrong card number or PIN!')
        menu()
    else:
        print('You have successfully logged in!')
        client_status = 'logged_in'
        active_session = card_number_input
        menu()


def log_out():
    global client_status
    client_status = 'logged_out'
    menu()


def exit_account():
    print('Bye!')


def card_exists(number):
    cur.execute("SELECT number FROM card WHERE number = {}".format(number))
    conn.commit()
    # gets the number of rows affected by the command executed
    row = cur.fetchone()
    if row is None:
        return False
    else:
        return True


def is_pin_valid(pin_code):
    cur.execute("SELECT pin FROM card WHERE pin = {}".format(pin_code))
    conn.commit()
    row = cur.fetchone()
    if row is None:
        return False
    else:
        return True


def has_enough_money_account(account, amount):
    cur.execute("SELECT balance FROM card WHERE number = {}".format(account))
    conn.commit()
    account_balance = cur.fetchone()[0]
    if int(amount) > account_balance:
        return False
    else:
        return True


def is_luhn_valid(number):
    card_number = list(number.strip())

    # Remove the last digit from the card number
    check_digit = card_number.pop()

    # Reverse the order of the remaining numbers
    card_number.reverse()

    processed_digits = []

    for index, digit in enumerate(card_number):
        if index % 2 == 0:
            doubled_digit = int(digit) * 2

            # Subtract 9 from any results that are greater than 9
            if doubled_digit > 9:
                doubled_digit = doubled_digit - 9

            processed_digits.append(doubled_digit)
        else:
            processed_digits.append(int(digit))

    total = int(check_digit) + sum(processed_digits)

    # Verify that the sum of the digits is divisible by 10
    if total % 10 == 0:
        return True
    else:
        return False


menu()