import mysql.connector
from mysql.connector import errorcode

print("Conectando...")
try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='igor',
        password='igor'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha')
    else:
        print(err)

cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS `routing`;")

cursor.execute("CREATE DATABASE `routing`;")

cursor.execute("USE `routing`;")

# criando tabelas
TABLES = {
    'tickets': ('''
        CREATE TABLE `zendesk_tickets` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `ticket_id` int(11) NOT NULL,
            `subject` varchar(150) NOT NULL,
            `channel` varchar(40) NOT NULL,
            `created_at` datetime NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')
}

for tabela_nome in TABLES:
    tabela_sql = TABLES[tabela_nome]
    try:
        print('Criando tabela {}:'.format(tabela_nome), end=' ')
        cursor.execute(tabela_sql)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('Tabela já existente')
        else:
            print(err.msg)
    else:
        print('Tabelas criadas com sucesso!')


# inserindo jogos
tickets_sql = 'INSERT INTO zendesk_tickets (ticket_id, subject, channel, created_at) VALUES (%s, %s, %s, %s)'
tickets = [
    ('9999', 'Ticket teste banco', 'Web', '2023-02-22 00:00:00')
]
cursor.executemany(tickets_sql, tickets)

cursor.execute('select * from routing.zendesk_tickets')
print(' -------------  Jogos:  -------------')
for ticket in cursor.fetchall():
    print(ticket[1])

# commitando se não nada tem efeito
conn.commit()

cursor.close()
conn.close()
