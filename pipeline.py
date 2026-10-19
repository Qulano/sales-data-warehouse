import sqlite3
from rich import print
import sys


def read_dataset(file_path):
    dataset = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            dataset.append(line.strip().split(","))
    return dataset


def transform(raw_data):
    header = raw_data[0]
    rows = raw_data[1:]
    seen_ids = []
    clean_rows = []
    for index, row in enumerate(rows, start =1):
        if len(row) == len(header) and "" not in row and row[0] not in seen_ids and row[1].isalpha() and row[2].isdigit() and "@" in row[3] and "." in row[3]:
            clean_rows.append((int(row[0]), row[1], int(row[2]), row[3]))
            seen_ids.append(row[0])
    return clean_rows


def transform_orders(raw_orders, valid_client_ids):
    header = raw_orders[0]
    rows = raw_orders[1:]
    clean_orders = []
    for index, row in enumerate(rows, start = 1):
        if len(row) == len(header) and "" not in row and row[1].isdigit() and row[2].isdigit() and int(row[2]) in valid_client_ids:
            clean_orders.append((row[0], int(row[1]), int(row[2])))
    return clean_orders
        
    
def load_to_db(clean_records, clean_orders, db_name = "warehouse.db"):
    with sqlite3.connect(db_name) as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS clients")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER,
                name TEXT,
                age INTEGER,
                email TEXT
            ) 
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                price INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders (client_id)")
        
        cursor.executemany('''
            INSERT INTO orders (item, price, client_id)
            VALUES (?, ?, ?)
        ''', clean_orders)

        cursor.executemany('''
            INSERT INTO clients (id, name, age, email)
            VALUES (?, ?, ?, ?)
        ''', clean_records)
    connection.close()
    print(f"[bold green]Успешно загружено в базу: {len(clean_records)} записей![/bold green]\n")
    
    
def generate_report(db_name = "warehouse.db"):
    with sqlite3.connect("warehouse.db") as connection:
        cur = connection.cursor()

        cur.execute("SELECT * FROM  clients")
        print("[bold yellow]Пользователи в базе данных[/bold yellow]")
        for row in cur.fetchall():
            print(row)

        cur.execute("SELECT clients.name, orders.item, orders.price FROM clients JOIN orders ON clients.id = orders.client_id")
        report_data = cur.fetchall()
        print("[bold yellow]Покупки[/bold yellow]")
        for row in report_data:
            print(row)
            
        cur.execute("SELECT clients.name, COUNT(orders.item), SUM(orders.price) FROM clients JOIN orders ON clients.id = orders.client_id GROUP BY clients.name")
        analytics_data = cur.fetchall()
        print("[bold yellow]Финансовая аналитика[/bold yellow]")
        for row in analytics_data:
            print(row)
    connection.close() 
    
       
def run_etl():
    records = read_dataset("dirty_data.csv")
    orders = read_dataset("dirty_orders.csv")
    clean_records = transform(records)
    valid_ids = [client[0] for client in clean_records]
    full_orders = transform_orders(orders, valid_ids)
    load_to_db(clean_records, full_orders)

if "--etl" in sys.argv:
    run_etl()
elif "--report" in sys.argv:
    generate_report()
else:
    run_etl()
    generate_report()
    










    