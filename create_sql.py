import random

sql = (
    'SET GLOBAL max_allowed_packet = 1000000000;' + '\n'
    'CREATE DATABASE IF NOT EXISTS exp;' + '\n'
    'USE exp;' + '\n'
    'DROP TABLE IF EXISTS exp;' + '\n'
    'CREATE TABLE exp (' + '\n'
    '  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,' + '\n'
    '  num1 int NOT NULL,' + '\n'
    '  num2 int NOT NULL,' + '\n'
    '  num3 int NOT NULL' + '\n'
    ');' + '\n'
)

sql += 'INSERT INTO exp(num1, num2, num3) VALUES '
l = []
record_num = 10 ** 6

for _ in range(record_num):
    n1 = random.randrange(10 ** 5)
    n2 = random.randrange(10 ** 3)
    n3 = random.randrange(10)
    l.append(f"({n1}, {n2}, {n3})")

sql += ','.join(l)

with open(f'./sql/{record_num}.sql', 'w') as f:
    f.write(sql)
