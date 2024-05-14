import sqlite3


def create_database(name):
    db = sqlite3.connect(name)
    db.row_factory = sqlite3.Row
    with open("db_struct.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


class DatabaseError(Exception):
    def __init__(self, *args):
        if args:
            self.message = "\n".join([str(i) for i in args])
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "DatabaseError has been raised"


class Database:
    def __init__(self, database=None):
        if database is None:
            database = sqlite3.connect("database.sqlite")
            database.row_factory = sqlite3.Row
        self.__db = database
        self.__cur = database.cursor()

    # members ------------------------------------------------------------------------------------------------------

    def get_user(self, telegram_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE telegram_id = ?",
                               (telegram_id,))
            step = self.__cur.fetchall()
            if not len(step):
                self.__add_user(telegram_id)
                return "start"
            return step[0]["step"]
        except Exception as exception:
            raise DatabaseError("Can't get user from database.", exception)

    def update_step(self, telegram_id, step):
        try:
            self.__cur.execute("UPDATE users SET step = ? WHERE telegram_id = ?", (step, telegram_id))
            self.__db.commit()
        except Exception as exception:
            raise DatabaseError("Can't update user's step.", exception)

    def get_photo(self, telegram_id):
        try:
            self.__cur.execute("SELECT photo FROM users WHERE telegram_id = ?", (telegram_id,))
            photo = self.__cur.fetchall()
            if not len(photo):
                return None
            return photo[0]["photo"]
        except Exception as exception:
            raise DatabaseError("Can't add user to database.", exception)

    def add_photo(self, telegram_id, path):
        try:
            self.__cur.execute("UPDATE users SET photo = ? WHERE telegram_id = ?", (path, telegram_id))
            self.__db.commit()
        except Exception as exception:
            raise DatabaseError("Can't add user to database.", exception)

    def __add_user(self, telegram_id):
        try:
            self.__cur.execute(f"INSERT INTO users VALUES (NULL, ?, '', 'step1')",
                               (telegram_id,))
            self.__db.commit()
        except Exception as exception:
            raise DatabaseError("Can't add user to database.", exception)


if __name__ == "__main__":
    # create_database("database.db")
    db = Database()
    db.get_user(2)
    print(db.get_user(2))
    db.add_photo(2, "path/to/photo.png")
    print(db.get_photo(2))