from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Nastav si tieto údaje podľa tvojej PostgreSQL konfigurácie
DB_HOST = 'localhost'
DB_NAME = 'Svet_puzzle'
DB_USER = 'postgres'
DB_PASSWORD = '2584695'  # <- nahraď za svoje skutočné heslo

def get_data_from_table(table_name):
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    if table_name == 'svet_puzzle_stat':
        cursor.execute('SELECT * FROM svet_puzzle_stat')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_okres':
        cursor.execute('SELECT * FROM svet_puzzle_okres')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_mesto':
        cursor.execute('SELECT * FROM svet_puzzle_mesto')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_partner':
        cursor.execute('SELECT * FROM svet_puzzle_partner')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_dotaznik':
        cursor.execute('SELECT * FROM svet_puzzle_dotaznik')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_odoslana_objednavka':
        cursor.execute('SELECT * FROM svet_puzzle_odoslana_objednavka')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_prijata_objednavka':
        cursor.execute('SELECT * FROM svet_puzzle_prijata_objednavka')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_tovar':
        cursor.execute('SELECT * FROM svet_puzzle_tovar')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_skupina_tovar':
        cursor.execute('SELECT * FROM svet_puzzle_skupina_tovar')
        data = cursor.fetchall()
    elif table_name == 'svet_puzzle_platba':
        cursor.execute('SELECT * FROM svet_puzzle_platba')
        data = cursor.fetchall()
    else:
        data = []
    cursor.close()
    conn.close()
    return data

@app.route('/', methods=['GET'])
def index():
    table = request.args.get('table', 'svet_puzzle_stat')  # predvolená tabuľka
    data = get_data_from_table(table)
    return render_template(
        'index.html',
        table=table,
        staty=data if table == 'svet_puzzle_stat' else None,
        okresy=data if table == 'svet_puzzle_okres' else None,
        mesta=data if table == 'svet_puzzle_mesto' else None,
        partneri=data if table == 'svet_puzzle_partner' else None,
        dotazniky=data if table == 'svet_puzzle_dotaznik' else None,
        odos_objednavky=data if table == 'svet_puzzle_odoslana_objednavka' else None,
        prij_objednavky=data if table == 'svet_puzzle_prijata_objednavka' else None,
        tovari=data if table == 'svet_puzzle_tovar' else None,
        skupina_tovari=data if table == 'svet_puzzle_skupina_tovar' else None,
        platby=data if table == 'svet_puzzle_platba' else None

    )

if __name__ == '__main__':
    app.run(debug=True)
