import sqlite3

def database_creator(cursor):
    cursor.execute('''CREATE TABLE subscribers
(subs_id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')

    cursor.execute('''CREATE TABLE maillist
(mail_id INTEGER PRIMARY KEY, name TEXT)''')

    cursor.execute('''CREATE TABLE maillist_to_subscribers
        (list_id INTEGER, subscriber_id INTEGER,
            FOREIGN KEY(list_id) REFERENCES maillist(mail_id),
            FOREIGN KEY(subscriber_id) REFERENCES subscribers(subs_id))''')


def main():

    conn = sqlite3.connect("mail_database.db")
    c = conn.cursor()
    database_creator(c)

if __name__ == '__main__':
    main()

