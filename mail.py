from commandparser import CommandParser
from maillist_factory import MailListFactory
from maillist_file_adapter import MailListFileAdapter
from glob import glob
from os.path import basename
import sys
import sqlite3


class MailListProgram():
    """docstring for MailListProgram"""
    def __init__(self):
        self.factory = MailListFactory()
        self.cp = CommandParser()
        self.lists = {}
        self.db_path = "lists/"

        self._load_initial_state()
        self._init_callbacks()
        self._loop()

    def create_list_callback(self, arguments):
        if len(str(arguments)) == 4:
            print("Invalid listname!")
        else:
            used_names = self.show_lists_callback("1")
            new_args = str(arguments)
            print (new_args[1:-1])
            for item in used_names:
                print (used_names)
            for item in used_names:
                if new_args[1:-1] == item:
                    print("asfsdfsaf")
            if new_args[1:-1] in used_names:
                print ("There is already a list with that name!")
            else:
                conn = sqlite3.connect("mail_list_database.db")
                cursor = conn.cursor()
                result = cursor.execute('''INSERT INTO maillist(name)
                                    VALUES (?)''', (arguments))
                conn.commit()
                conn.close()


    def add_subscriber_callback(self, arguments):
        list_id = arguments[0]
        conn = sqlite3.connect("mail_list_database.db")
        cursor = conn.cursor()
        name = input("name>")
        email = input("email>")
        result1 = cursor.execute('''SELECT subs_id
                                    FROM subscribers
                                    WHERE name = ? and email = ?''', (name, email))
        final_res = cursor.fetchone()
        if final_res is None:
            print(cursor.fetchone())
            result2 = cursor.execute('''INSERT INTO subscribers(name, email)
                                        VALUES(?, ?)''', (name, email))

            result3 = cursor.execute('''SELECT subs_id
                                        FROM subscribers
                                        WHERE name = ? and email = ?''', (name, email))
            result_from_3rd_query = cursor.fetchone()
            res3 = int(result_from_3rd_query[0])

            result4 = cursor.execute(''' INSERT INTO maillist_to_subscribers(list_id, subscribesr_id)
                                        VALUES (?, ?)''', (list_id, res3))
        else:
            result_from_1st_query = final_res
            res1 = int(result_from_1st_query[0])
            result5 = cursor.execute('''SELECT list_id
                                        FROM maillist_to_subscribers
                                        WHERE subscribesr_id = (?)''', str(res1))
            lists = []
            for row in result5:
                lists.append(int(row[0]))
            if int(list_id) in lists:
                print ("The subscriber is already in that list")
            else:
                result6 = cursor.execute('''INSERT INTO maillist_to_subscribers(list_id, subscribesr_id)
                                            VALUES (?,?)''', (list_id, res1) )
        conn.commit()
        conn.close()

    def show_lists_callback(self, want_return=0):
        conn = sqlite3.connect("mail_list_database.db")
        cursor = conn.cursor()
        list_names = []
        list_ids = []
        result = cursor.execute("SELECT * FROM maillist")
        for row in result:
            list_ids.append(row[0])
            list_names.append(row[1])
        conn.close()
        the_wish = len(want_return)
        if the_wish == 0:
            for row in range(0, len(list_ids)):
                print(str(list_ids[row]) + " - " + list_names[row])
        else:
            return(list_names)


    def show_list_callback(self, arguments):
        conn = sqlite3.connect("mail_list_database.db")
        cursor = conn.cursor()

        used_names = self.show_lists_callback("1")
        integer_argument = int(arguments[0])
        if integer_argument > len(used_names):
            print ("There is no list with this identifier!")
        else:
            result = cursor.execute('''SELECT DISTINCT subscribers.subs_id, subscribers.name, subscribers.email
                FROM subscribers INNER JOIN maillist_to_subscribers ON subscribers.subs_id = maillist_to_subscribers.subscribesr_id
                INNER JOIN maillist ON maillist_to_subscribers.list_id = ?''', (arguments))
            for row in result:
                print(row)
            conn.commit()
            conn.close()


    def exit_callback(self, arguments):
        sys.exit(0)

    def _load_initial_state(self):
        dir_lists = map(basename, glob(self.db_path + "*"))

        for list_file in dir_lists:
            adapter = MailListFileAdapter(self.db_path)
            parsed_list = adapter.load(list_file)

            maillist_adapter = MailListFileAdapter(self.db_path, parsed_list)

            self.lists[parsed_list.get_id()] = (parsed_list, maillist_adapter)

    def _init_callbacks(self):
        self.cp.on("create", self.create_list_callback)
        self.cp.on("add", self.add_subscriber_callback)
        self.cp.on("show_lists", self.show_lists_callback)
        self.cp.on("show_list", self.show_list_callback)
        self.cp.on("exit", self.exit_callback)
        # TODO - implement the rest of the callbacks

    def _notify_save(self, list_id):
        self.lists[list_id][1].save()

    def _loop(self):
        while True:
            command = input(">")
            self.cp.take_command(command)


if __name__ == '__main__':
    MailListProgram()
