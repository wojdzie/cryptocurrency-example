from app import mysql, session
from blockchain import Blockchain, Block


class InvalidTransactionException(Exception): pass


class InsufficientFundsException(Exception): pass


class Table:
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(" + ','.join(args) + ")"
        self.columnsList = args

        if is_new_table(table_name):
            created_data = ""

            for column in self.columnsList:
                created_data += f"{column} varchar(100),"

            cur = mysql.connection.cursor()
            cur.execute(f"CREATE TABLE {self.table}({created_data[:len(created_data) - 1]})")
            cur.close()

    def get_all(self):
        cur = mysql.connection.cursor()
        result = cur.execute(f"SELECT * FROM {self.table}")
        data = cur.fetchall()
        return data

    def get_one(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute(f"SELECT * FROM {self.table} WHERE {search} = \"{value}\"")
        if result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    def delete_one(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE {search} = \"{value}\"")
        mysql.connection.commit()
        cur.close()

    def delete_all(self):
        self.drop()
        self.__init__(self.table, *self.columnsList)

    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute(f"DROP TABLE {self.table}")
        cur.close()

    def insert(self, *args):
        data = ""
        for arg in args:
            data += f"\"{arg}\","

        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO {self.table} {self.columns} VALUES({data[:len(data) - 1]})")
        mysql.connection.commit()
        cur.close()


def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()


def is_new_table(table_name):
    cur = mysql.connection.cursor()

    try:
        result = cur.execute(f"SELECT * from {table_name}")
        cur.close()
    except:
        return True
    else:
        return False


def is_new_user(username):
    users = Table("users", "name", "email", "username", "password")
    data = users.get_all()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True


def send_money(sender, recipient, amount):
    try:
        amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.")

    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient Funds.")
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException("Invalid Transaction")
    elif is_new_user(recipient):
        raise InvalidTransactionException("User Does Not Exist.")

    blockchain = get_blockchain()
    number = len(blockchain.chain) + 1
    data = f"{sender}-->{recipient}-->{amount}"
    blockchain.mine(Block(number, data=data))
    sync_blockchain(blockchain)


def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()
    for block in blockchain.chain:
        data = block.data.split("-->")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance


def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", "number", "hash", "previous_hash", "data", "nonce")
    for b in blockchain_sql.get_all():
        blockchain.add(Block(int(b.get('number')), b.get('previous_hash'), b.get('data'), int(b.get('nonce'))))

    return blockchain


def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number", "hash", "previous_hash", "data", "nonce")
    blockchain_sql.delete_all()

    for block in blockchain.chain:
        blockchain_sql.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)
