# Write your code here
import random
import sqlite3
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

curAccount = None


def generate_number(length):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def luhn_algorithm(number):
    orig_number = number
    number = list(map(int, number))
    for index, _ in enumerate(number):
        if index % 2 == 0:
            number[index] *= 2
            if number[index] > 9:
                number[index] -= 9
    orig_number += str((10 - sum(number) % 10) % 10)
    return int(orig_number)


class BankAccount:
    def __init__(self):
        self.id = int(generate_number(16))
        self.card_number = luhn_algorithm('400000' + generate_number(9))
        self.pin = generate_number(4)
        self.balance = 0


# cur.execute('CREATE TABLE card('
#             'id INTEGER,'
#             'number TEXT,'
#             'pin TEXT,'
#             'balance INTEGER DEFAULT 0'
#             ')')
# conn.commit()
# cur.execute('DELETE FROM card')
# conn.commit()
while True:
    if curAccount:
        print("1. Balance\n"
              "2. Add income\n"
              "3. Do transfer\n"
              "4. Close account\n"
              "5. Log out\n"
              "0. Exit")
        inp = int(input())
        if inp == 1:
            print("Balance:", curAccount[3])
        elif inp == 2:
            print("Enter income:")
            curAccount[3] += int(input())
            cur.execute('UPDATE card SET balance=? WHERE id=?', (curAccount[3], curAccount[0]))
            conn.commit()
            print("Income was added!")
        elif inp == 3:
            print("Transfer\n"
                  "Enter card number:")
            transfer_card = input()
            if luhn_algorithm(transfer_card[:-1]) != int(transfer_card):
                print("Probably you made a mistake in the card number.\n"
                      "Please try again!")
            else:
                cur.execute('SELECT * FROM card WHERE number=?', (transfer_card, ))
                secAccount = cur.fetchone()
                if secAccount is None:
                    print("Such a card does not exist.")
                elif secAccount[1] == curAccount[1]:
                    print("You can't transfer money to the same account!")
                else:
                    print("Enter how much money you want to transfer:")
                    deposit = int(input())
                    if deposit > curAccount[3]:
                        print("Not enough money!")
                    else:
                        cur.execute('UPDATE card SET balance=balance+? WHERE number=?', (deposit, secAccount[1]))
                        cur.execute('UPDATE card SET balance=balance-? WHERE id=?', (deposit, curAccount[0]))
                        conn.commit()
                        curAccount[3] -= deposit
                        print("Success!")
        elif inp == 4:
            cur.execute('DELETE FROM card WHERE id=?', (curAccount[0], ))
            conn.commit()
            curAccount = None
            print("The account has been closed!")
        elif inp == 5:
            curAccount = None
            print("You have successfully logged out!")
        else:
            break
    else:
        print("1. Create an account\n"
              "2. Log into account\n"
              "0. Exit")
        inp = int(input())
        if inp == 1:
            new = BankAccount()
            cur.execute('INSERT INTO card (id, number, pin) VALUES (?, ?, ?)',
                        (new.id, new.card_number, new.pin))
            conn.commit()
            print(f"Your card has been created\n"
                  f"Your card number:\n"
                  f"{new.card_number}\n"
                  f"Your card PIN:\n"
                  f"{new.pin}")
        elif inp == 2:
            print("Enter your card number:")
            user_card_number = int(input())
            print("Enter your PIN:")
            user_pin = input()
            cur.execute('SELECT * FROM card WHERE number=? AND pin=?', (user_card_number, user_pin))
            curAccount = cur.fetchone()
            if curAccount is not None:
                curAccount = list(curAccount)
                print("You have successfully logged in!")
            else:
                print("Wrong card number or PIN!")
        else:
            break
print("Bye!")
