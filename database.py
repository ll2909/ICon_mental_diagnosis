import mysql.connector
import pymysql as sql
import numpy as np
import pandas as pd

def mySQLConnect(hostname, username, pw):
    """
    Funzione che crea la connessione a MySQL
    
    Parameters
    ----------
    hostname: str
        Nome dell'host del db server
    username: str
        Username di accesso
    password: str
        Password di accesso
    Returns
    -------
    conn: connection
        Connessione a MySQL
    """

    # Hostname usually is localhost, default username is root
    return mysql.connector.connect(host = hostname, user = username, password = pw)

def createDatabase(conn, dbName):
    """
    Funzione che crea il database, se non esiste, e automaticamente selezionato

    Parameters
    ----------
    conn: connection
        Connessione al database
    dbName: str
        Nome del database
    """
    sql.install_as_MySQLdb()

    cursor = conn.cursor()
    
    try:
        cursor.execute("""CREATE DATABASE IF NOT EXISTS """ + dbName + """;""")
        conn.commit()
    except sql.ProgrammingError:
        pass
    cursor.close()
    useDatabase(conn,dbName)

def useDatabase(conn, dbName):
    """
    Funzione che seleziona il database da utilizzare

    Parameters
    ----------
    conn: connection
        Connessione al database
    dbName: str
        Nome del database
    
    """
    cursor = conn.cursor()
    cursor.execute(cursor.execute("""USE """+ dbName +""";"""))
    conn.commit()

def checkIfDbExists(conn, db_name):
    """
    Funzione che verifica l'esistenza del database

    Parameters
    ----------
    conn: connection
        Connessione al database
    dbName: str
        Nome del database

    Returns
    -------
    boolean
        True se il database esiste, false altrimenti
    """
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    res = False
    for db in cursor.fetchall():
        if db[0] == db_name:
            print("Database ", db_name, " exists.")
            res = True
    return res

def createTablefromFile(filename, tablename, conn):
    """
    Funzione che crea una tabella e la popola con i valori all'interno
    del file csv in input

    Parameters
    ----------
    filename: str
        Nome/percorso del file csv da aprire
    tablename: str
        Nome della tabella da creare
    conn: connection
        Connessione al database
    """
    sql.install_as_MySQLdb()

    cursor = conn.cursor()  
    dropTable = """DROP TABLE IF EXISTS """ + tablename + """;"""

    data = pd.DataFrame(pd.read_csv(filename))

    # Costruzione query di creazione tabella e inserimento dati

    createTable = """CREATE TABLE """ + tablename + """("""
    insertInto = """INSERT INTO """ + tablename + """("""
    insertValues = """VALUES ("""

    toInsert = []

    for col in data.columns:
        createTable += col + """ VARCHAR(100),""" 
        insertInto += col + ""","""
        insertValues += """LOWER(%s),"""

    createTable = createTable[:-1] + """);"""
    insertValues = insertValues[:-1] + """)""" #
    insertInto = insertInto[:-1] + """) """ + insertValues
    try:
        cursor.execute(dropTable)
        cursor.execute(createTable)
    except sql.ProgrammingError:
        pass

    for tuple in data.itertuples(False, None):
        print("Inserted", tuple)
        cursor.execute(insertInto, tuple)
        conn.commit()
    print("Created ", tablename, " table.")
    cursor.close()
    
    
def getValue(conn, table, col, value):
    """
    Funzione che restituisce l'id di un valore all'interno di una tabella, in un preciso campo

    Parameters
    ----------
    conn: connection
        Connessione al database
    table: str
        Nome della tabella
    col: str
        Nome del campo
    value: str
        Valore da verificare

    Returns
    -------
    result: str
        Stringa contenente l'id del valore
    """
    cursor = conn.cursor(buffered = True)
    query = """SELECT id FROM """ + table + """ WHERE """ + col + """ LIKE '%""" + value + """%';"""
    cursor.execute(query)
    result = cursor.fetchall()
    result = result[0][0]
    return result

def ifValueExists(conn, table, col, value):
    """
    Funzione che verifica l'esistenza di un valore all'interno di una tabella, in un preciso campo

    Parameters
    ----------
    conn: connection
        Connessione al database
    table: str
        Nome della tabella
    col: str
        Nome del campo
    value: str
        Valore da verificare
    Returns
    -------
    boolean
        True se il valore esiste, false altrimenti
    """

    cursor = conn.cursor(buffered = True)
    query = """SELECT id FROM """ + table + """ WHERE """ + col + """='""" + value + """';"""
    cursor.execute(query)
    check = cursor.fetchall()
    if not check:
        return False
    else:
        return True

def selectJoinID(conn, data, table1, table2, v1, v2):
    """
    Funzione che effettua un right join tra due tabelle, restituendo una lista contenente i valori in comune
    tra la prima e la seconda tabella, data una lista di valori in input

    Parameters
    ----------
    conn: connection
        Connessione al database
    data: list
        Lista dei valori
    table1: str
        Nome della prima tabella
    table2: str
        Valore della seconda tabella
    v1: str
        Campo criterio da verificare
    v2: str
        Campo da selezionare
    Returns
    -------
    id_1: list
        Lista contenente i valori della seconda tabella in comune con quelli della prima
    """

    cursor = conn.cursor(buffered = True)
    id_1 = []
    id_2 = []
    
    for i in data:
        # Selezione id della prima tabella
        query1 = """SELECT DISTINCT id FROM """ + table1 + """ WHERE name='""" + i +"""';""" 
        cursor.execute(query1)
        id_2.append(cursor.fetchall()) 
     
    for i in id_2:
        # Selezione id della seconda tablella in cui gli id di table1 sono uguali ai valori di v2 in table2
        query2 = """SELECT """ + v2 + """ FROM """ + table2 + """ WHERE """ + v1 + """='"""+ i[0][0] +"""';"""
        cursor.execute(query2)
        id_1.append(cursor.fetchall())
    
    return id_1

def getNameFromID(conn, table, id):
    """
    Funzione che restituisce il nome della tupla all'interno di una specifica tabella, con
    uno specifico id

    Parameters
    ----------
    conn: connection
        Connesisone al database
    table: str
        Nome della tabella
    id: str
        Id della tupla
    Returns
    -------
    cursor: str
        Nome della tupla
    """
    cursor = conn.cursor(buffered = True)
    query = """SELECT name FROM """ + table + """ WHERE id ='""" + id + """';"""
    cursor.execute(query) 
    cursor = cursor.fetchall()
    cursor = cursor[0][0]
    if "_" in cursor:
        pos = cursor.index("_")
        cursor = cursor[0:pos]
    return cursor

def getValueCategory(conn, table, value):
    """
    Funzione che restituisce una stringa contenenta le categoria del valore di una specifica tabella

    Parameters
    ----------
    conn: connection
        Connesisone al database
    table: str
        Nome della tabella
    values: str
        Nome della tupla

    Returns
    -------
    cursor: str
        Categoria del campo della rispettiva tabella
    """
    query = """SELECT category FROM """ + table + """ WHERE id = '""" + value + """';"""
    cursor = conn.cursor(buffered = True)
    cursor.execute(query)
    cursor = cursor.fetchall()
    return cursor[0]

def getValuesCategory(conn, table, list_values):
    """
    Funzione che restituisce una lista contenente le categorie dei valori di una specifica tabella

    Parameters
    ----------
    conn: connection
        Connesisone al database
    table: str
        Nome della tabella
    list_values: list
        Lista contenenti i nomi delle tuple

    Returns
    -------
    cat: list
        Lista contenenti le categorie dei campi della rispettiva tabella
    """
    cursor = conn.cursor(buffered = True)
    cat = []
    
    for i in list_values:

        query = """SELECT category FROM """ + table + """ WHERE name='""" + i +"""';""" 
        cursor.execute(query)
        cat.append(cursor.fetchall())
    
    return cat

def closeConnection(conn):
    """
    Funzione che chiude la connessione al database

    Parameters
    ----------
    conn: connection
        Connessione al database
    """
    conn.close()