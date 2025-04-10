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

@app.route('/select', methods=['GET', 'POST'])
def select():
    zisk = None
    rows = []
    selected_fields = []
    fields = []

    if request.method == 'POST':
        stat = request.form.get('stat')
        okres = request.form.get('okres')
        mesto = request.form.get('mesto')
        tovar = request.form.get('tovar')
        partner = request.form.get('partner')
        skupina = request.form.get('skupina')
        rok = request.form.get('roky')
        pravna_forma = request.form.get('pravna_forma')

        field_mapping = {
            'stat': ('h.nazov_statu', stat),
            'okres': ('g.nazov_okr', okres),
            'mesto': ('f.nazov_mesto', mesto),
            'tovar': ('b.nazov_tovar', tovar),
            'partner': ('e.meno_partner', partner),
            'skupina': ('a.nazov_skup', skupina)
        }

        # Vezmeme len tie, čo nie sú "-"
        selected_fields = [v[0] for k, v in field_mapping.items() if v[1] != '-']
        group_by_sql = ", ".join(selected_fields) if selected_fields else "1"
        
        select_sql = group_by_sql + "," if selected_fields else ""


        # Základný SQL dotaz
        query = f"""
            SELECT {select_sql}
            ROUND(SUM(c.mnozstvo_tovaru * b.predaj_cena)::numeric, 2) AS prijem,
            ROUND(SUM(c.mnozstvo_tovaru * b.nakup_cena)::numeric, 2) AS naklady,
            ROUND(SUM((b.predaj_cena - b.nakup_cena) * c.mnozstvo_tovaru)::numeric, 2) AS zisk
            FROM svet_puzzle_skupina_tovar a
            JOIN svet_puzzle_tovar b ON a.id_typ_tovar = b.id_typ_tovar
            JOIN svet_puzzle_odoslana_objednavka c ON b.id_tovar = c.id_tovar
            JOIN svet_puzzle_partner e ON c.id_partner = e.id_partner
            JOIN svet_puzzle_mesto f ON e.skr_mesto = f.skr_mesto
            JOIN svet_puzzle_okres g ON f.skr_okr = g.skr_okr
            JOIN svet_puzzle_stat h ON g.skr_stat = h.skr_stat
        """

        conditions = []

            # Pridaj filter na rok, ak je zadaný
        if rok != '-':
            conditions.append(f"EXTRACT(YEAR FROM c.datum_obj) = {rok}")

        # Pridaj filter na právnu formu, ak nie je "vsetky"
        if pravna_forma in ['F_os', 'P_os']:
            conditions.append(f"e.pravna_forma = '{pravna_forma}'")
            

            # Ak existujú podmienky, pridaj WHERE klauzulu
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # GROUP BY
        query += f" GROUP BY {group_by_sql}"

        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()


        # Ak nie sú vybrané žiadne group by polia – zobraz len celkový zisk
        if not selected_fields and rows:
            zisk = {
                "prijem": rows[0][0],
                "naklady": rows[0][1],
                "zisk": rows[0][2]
            }

            # Prázdne group by polia, ale nech to funguje s výstupom
            fields = []
            rows = []  # Nechceš tabuľku pri celkovom zisku

        else:
            # Pre tabuľku – pridaj aj 3 fixné výstupné polia
            fields = selected_fields + ["prijem", "naklady", "zisk"]

        cur.close()
        conn.close()

    return render_template('select.html', zisk=zisk, rows=rows, fields=fields)



@app.route('/form', methods=['GET'])
def form():
    return render_template('form.html')  # Just render the form when GET request is made

@app.route('/submit', methods=['POST'])
def submit():
    tabulka = request.form.get("tabulka")
    conn = psycopg2.connect(
                        host=DB_HOST,
                        dbname=DB_NAME,
                        user=DB_USER,
                        password=DB_PASSWORD
                    )
    
    cur = conn.cursor()


    try:

        if tabulka == "svet_puzzle_stat":
            data = {
                'skr_stat': request.form.get('skratka_stat'),
                'nazov_statu': request.form.get('stat-nazov'),
                'pocet_obyvatelov': request.form.get('stat-obyvatelia'),
                'rozloha': request.form.get('stat-rozloha'),
                'popis': request.form.get('stat-popis'),
                'hustota': request.form.get('stat-hustota')
            }

            cur.execute("""
                INSERT INTO svet_puzzle_stat (skr_stat, nazov_statu, pocet_obyvatelov, rozloha, popis, hustota)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['skr_stat'], data['nazov_statu'], data['pocet_obyvatelov'], data['rozloha'], data['popis'], data['hustota']))
        
        elif tabulka == "svet_puzzle_okres":
            data = {
                'skr_okr': request.form.get('skratka-okres'),
                'nazov_okr': request.form.get('okres-nazov'),
                'pocet_obyvatelov': request.form.get('okres-obyvatelia'),
                'rozloha': request.form.get('okres-rozloha'),
                'popis': request.form.get('okres-popis'),
                'hustota': request.form.get('okres-hustota'),
                'skr_stat': request.form.get('okres-id-stat'),
            }

            cur.execute("""
                INSERT INTO svet_puzzle_okres (skr_okr, nazov_okr, pocet_obyvatelov, rozloha, popis, hustota, skr_stat)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data['skr_okr'], data['nazov_okr'], data['pocet_obyvatelov'], data['rozloha'], data['popis'], data['hustota'], data['skr_stat']))

        
        elif tabulka == "svet_puzzle_mesto":
            data = {
                'skr_mesto': request.form.get('mesto-id'),
                'nazov_mesto': request.form.get('mesto-nazov'),
                'pocet_obyvatelov': request.form.get('mesto-obyvatelia'),
                'rozloha': request.form.get('mesto-rozloha'),
                'popis': request.form.get('mesto-popis'),
                'hustota': request.form.get('mesto-hustota'),
                'skr_okr': request.form.get('mesto-id-okres'),

            }

            cur.execute("""
                INSERT INTO svet_puzzle_mesto (skr_mesto, nazov_mesto, pocet_obyvatelov, rozloha, popis, hustota, skr_okr)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data['skr_mesto'], data['nazov_mesto'], data['pocet_obyvatelov'], data['rozloha'], data['popis'], data['hustota'], data['skr_okr']))

        elif tabulka == "svet_puzzle_partner":
            data = {
                'id_partner': request.form.get('partner-id'),
                'meno_partner': request.form.get('partner-meno'),
                'pravna_forma': request.form.get('pravna-forma'),
                'skr_mesto': request.form.get('partner-id-mesto'),
                'ulica': request.form.get('partner-ulica'),
                'psc': request.form.get('partner-psc'),
                'tel': request.form.get('partner-tel'),
                'email': request.form.get('partner-email'),

            }

            cur.execute("""
                INSERT INTO svet_puzzle_partner (id_partner, meno_partner, pravna_forma, skr_mesto, ulica, psc, tel, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['id_partner'], data['meno_partner'], data['pravna_forma'], data['skr_mesto'], data['ulica'], data['psc'], data['tel'], data['email']))
        
        elif tabulka == "svet_puzzle_dotaznik":
            data = {
                'id_dotaznik': request.form.get('dotaznik-id'),
                'id_partner': request.form.get('dotaznik-id-partner'),
                'spokojnost_proces': request.form.get('dotaznik-spoko-proces'),
                'spokojnost_komunikacia': request.form.get('dotaznik-spoko-komuni'),
                'prehladnost_eshop': request.form.get('dotaznik-preh-eshop'),
                'zdrojovy_kanal': request.form.get('dotaznik-zdroj-kanal'),
                'napady_na_zlepsenie': request.form.get('mesto-id-okres'),
                'vek': request.form.get('dotaznik-vek'),

            }

            cur.execute("""
                INSERT INTO svet_puzzle_dotaznik (id_dotaznik, id_partner, spokojnost_proces, spokojnost_komunikacia, prehladnost_eshop, zdrojovy_kanal, napady_na_zlepsenie, vek)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['id_dotaznik'], data['id_partner'], data['spokojnost_proces'], data['spokojnost_komunikacia'], data['prehladnost_eshop'], data['zdrojovy_kanal'], data['napady_na_zlepsenie'], data['vek']))
        
        elif tabulka == "svet_puzzle_odoslana_objednavka":
            data = {
                'id_odos_obj': request.form.get('odos_obj-id'),
                'id_partner': request.form.get('odos_obj-id-partner'),
                'datum_obj': request.form.get('odos_obj-datum-objednania'),
                'datum_dod': request.form.get('odos_obj-datum-dodania'),
                'mnozstvo_tovaru': request.form.get('odos_obj-mnozstvo-tovaru'),
                'id_tovar': request.form.get('odos_obj-id-tovar'),
                'zlava': request.form.get('odos_obj-zlava'),
                'id_platba': request.form.get('odos_obj-id-platba'),
                'id_faktura': request.form.get('odos_obj-faktura'),


            }

            cur.execute("""
                INSERT INTO svet_puzzle_odoslana_objednavka (id_odos_obj, id_partner, datum_obj, datum_dod, mnozstvo_tovaru, id_tovar, zlava, id_platba, id_faktura)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['id_odos_obj'], data['id_partner'], data['datum_obj'], data['datum_dod'], data['mnozstvo_tovaru'], data['id_tovar'], data['zlava'], data['id_platba'], data['id_faktura']))
        
        elif tabulka == "svet_puzzle_prijata_objednavka":
            data = {
                'id_prij_obj': request.form.get('prij_obj-id'),
                'id_partner': request.form.get('prij_obj-id-partner'),
                'datum_obj': request.form.get('prij_obj-datum-objednania'),
                'datum_dod': request.form.get('prij_obj-datum-dodania'),
                'mnozstvo_tovaru': request.form.get('prij_obj-mnozstvo-tovaru'),
                'id_tovar': request.form.get('prij_obj-id-tovar'),
                'id_platba': request.form.get('prij_obj-id-platba'),
                'id_faktura': request.form.get('prij_obj-faktura'),


            }

            cur.execute("""
                INSERT INTO svet_puzzle_prijata_objednavka (id_prij_obj, id_partner, datum_obj, datum_dod, mnozstvo_tovaru, id_tovar, id_platba, id_faktura)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['id_prij_obj'], data['id_partner'], data['datum_obj'], data['datum_dod'], data['mnozstvo_tovaru'], data['id_tovar'], data['id_platba'], data['id_faktura']))
        
        elif tabulka == "svet_puzzle_tovar":
            data = {
                'id_tovar': request.form.get('tovar-id'),
                'nazov_tovar': request.form.get('tovar-nazov'),
                'nakup_cena': request.form.get('tovar-nakup-cena'),
                'predaj_cena': request.form.get('tovar-predaj-cena'),
                'ocakavana_marza': request.form.get('tovar-oc-marza'),
                'hmotnost': request.form.get('tovar-hmotnost'),
                'popis': request.form.get('tovar-popis'),
                'vyrobca': request.form.get('tovar-vyrobca'),
                'id_typ_tovar': request.form.get('tovar-ID-typ-tovar'),


            }

            cur.execute("""
                INSERT INTO svet_puzzle_tovar (id_tovar, nazov_tovar, nakup_cena, predaj_cena, ocakavana_marza, hmotnost, popis, vyrobca, id_typ_tovar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['id_tovar'], data['nazov_tovar'], data['nakup_cena'], data['predaj_cena'], data['ocakavana_marza'], data['hmotnost'], data['popis'], data['vyrobca'], data['id_typ_tovar']))

        elif tabulka == "svet_puzzle_platba":
            data = {
                'id_platba': request.form.get('platba-id'),
                'sposob_dopravy': request.form.get('platba-s-dopravy'),
                'cena_dopravy': request.form.get('platba-cena-dopravy'),
                'cena_platby': request.form.get('platba-cena-platby'),
                'komentar': request.form.get('platba-komentar'),
                'id_partner': request.form.get('platba-ID-partner'),
               


            }

            cur.execute("""
                INSERT INTO svet_puzzle_platba (id_platba, sposob_dopravy, cena_dopravy, cena_platby, komentar, id_partner)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['id_platba'], data['sposob_dopravy'], data['cena_dopravy'], data['cena_platby'], data['komentar'], data['id_partner']))
        
        elif tabulka == "svet_puzzle_skupina_tovar":
            data = {
                'id_typ_tovar': request.form.get('skupina_tovar-id'),
                'popis_skupiny': request.form.get('skupina_tovar-popis'),
                'nazov_skup': request.form.get('skupina_tovar-nazov'),
                

            }
            cur.execute("""
                INSERT INTO svet_puzzle_skupina_tovar (id_typ_tovar, popis_skupiny, nazov_skup)
                VALUES (%s, %s, %s)
            """, (data['id_typ_tovar'], data['popis_skupiny'], data['nazov_skup']))
      
        else:
            return "Neplatná tabuľka", 400

        conn.commit()
        return "Dáta úspešne vložené!"

    except Exception as e:
        if tabulka == "svet_puzzle_stat":
            return "Neplatná tabuľka alebo chyba pri vkladaní štátu.", 500
        elif tabulka == "svet_puzzle_okres":
            return "Chýbajúce údaje v tabuľke štát alebo daný okres už je zadaný. Najprv vyplňte formulár pre príslušný štát.", 500
        elif tabulka == "svet_puzzle_mesto":
            return "Chýbajúce údaje v tabuľke okres alebo dané mesto už je zadané. Najprv vyplňte formulár pre príslušný okres.", 500
        elif tabulka == "svet_puzzle_partner":
            return "Chýbajúce údaje v tabuľke mesto alebo číslo partnera už existuje. Najprv vyplňte formulár pre príslušný mesto.", 500
        elif tabulka == "svet_puzzle_dotaznik":
            return "Chýbajúce údaje v tabuľke partner alebo číslo dotazníka už existuje. Najprv vyplňte formulár pre príslušný mesto.", 500
        elif tabulka == "svet_puzzle_odoslana_objednavka":
             return "Chýbajúce údaje v tabuľke odoslaná objednavka alebo ID odoslanej objednávky už existuje. Najprv vyplňte formulár pre príslušný tovar,partnera, platbu.", 500
        elif tabulka == "svet_puzzle_prijata_objednavka":
             return "Chýbajúce údaje v tabuľke prijatá objednavka alebo ID prijatej objednávky už existuje. Najprv vyplňte formulár pre príslušný tovar,partnera, platbu.", 500
        elif tabulka == "svet_puzzle_tovar":
          return "Chýbajúce údaje v tabuľke tovar alebo ID tovar už existuje. Najprv vyplňte formulár pre príslušný ID typ tovaru", 500
        elif tabulka == "svet_puzzle_platba":
            return "Chýbajúce údaje v tabuľke platba alebo ID platba už existuje. Najprv vyplňte formulár pre príslušný ID partner", 500
        elif tabulka == "svet_puzzle_skupina_tovar":
            return "Chýbajúce údaje v tabuľke skupina tovar alebo ID typ tovar už existuje.", 500
        
        else:
            return f"Chyba pri vkladaní dát: {e}", 500
    finally:
        cur.close()
        conn.close()


@app.route('/delete', methods=['GET'])
def delete():
    return render_template('delete.html')  # Just render the form when GET request is made
@app.route('/submit_delete', methods=['POST'])
def submit_delete():
    tabulka = request.form.get("tabulka")
    record_id = request.form.get("id")  # Get the ID of the record to delete

    if not tabulka or not record_id:
        return "Tabuľka alebo ID záznamu nie je zadané.", 400

    conn = psycopg2.connect(
                        host=DB_HOST,
                        dbname=DB_NAME,
                        user=DB_USER,
                        password=DB_PASSWORD
                    )
    
    cur = conn.cursor()

    try:

        id_stlpce = {
            "svet_puzzle_stat": "skr_stat",
            "svet_puzzle_okres": "skr_okr",
            "svet_puzzle_mesto": "skr_mesto",
            "svet_puzzle_partner": "id_partner",
            "svet_puzzle_dotaznik": "id_dotaznik",
            "svet_puzzle_odoslana_objednavka": "id_odos_obj",
            "svet_puzzle_prijata_objednavka": "id_prij_obj",
            "svet_puzzle_tovar": "id_tovar",
            "svet_puzzle_platba": "id_platba",
            "svet_puzzle_skupina_tovar": "id_typ_tovar"
        }
        if tabulka not in id_stlpce:
            return "Neplatná tabuľka", 400
                
        id_stlpec = id_stlpce[tabulka]
        cur.execute(f"SELECT 1 FROM {tabulka} WHERE {id_stlpec} = %s", (record_id,))
        if cur.fetchone() is None:
            return f"Záznam s ID '{record_id}' v tabuľke '{tabulka}' neexistuje.", 404
        cur.execute(f"DELETE FROM {tabulka} WHERE {id_stlpec} = %s", (record_id,))
        conn.commit()
        return "Dáta úspešne vymazané!"
    except Exception as e:
        if tabulka == "svet_puzzle_stat":
            return "Neplatná tabuľka alebo chyba pri vymazávaní štátu.", 500
        elif tabulka == "svet_puzzle_okres":
            return "Najprv vymaž príslušný štát k danému okresu", 500
        elif tabulka == "svet_puzzle_mesto":
            return "Najprv vymaž príslušný okres k danému mestu.", 500
        elif tabulka == "svet_puzzle_partner":
            return "Najprv vymaž príslušné mesto k danému partnerovi. ", 500
        elif tabulka == "svet_puzzle_dotaznik":
            return "Najprv vymaž príslušného partnera k danému dotazníku.", 500
        elif tabulka == "svet_puzzle_odoslana_objednavka":
             return "Najprv vymaž príslušný tovar,partnera, platbu pre príslušnú ID_odos_objednavka .", 500
        elif tabulka == "svet_puzzle_prijata_objednavka":
             return "Najprv vymaž príslušný tovar,partnera, platbu pre príslušnú ID_prij_objednavka", 500
        elif tabulka == "svet_puzzle_tovar":
          return "Najprv vymaž príslušnú ID_skup_tovar k príslušnému tovaru ", 500
        elif tabulka == "svet_puzzle_platba":
            return "Najprv vymaž partnera k príslušnej platbe", 500
        elif tabulka == "svet_puzzle_skupina_tovar":
            return "Neplatná tabuľka alebo chyba pri vymazávaní skupiny tovaru .", 500
        else:
            return f"Chyba pri vkladaní dát: {e}", 500

    finally:
        cur.close()
        conn.close()



if __name__ == '__main__':
    app.run(debug=True)






  






