import BBN
import mysql.connector
import database
import pandas as pd
from collections import Counter
from collections import defaultdict
import xml_parser as xml

def inputSymptoms(conn):
    """
    Funzione per inserire i sintomi dell'utente

    Parameters
    ----------
    conn: connection
        Connessione al database. Usato per verificare che l'input sia corretto
    
    Returns
    -------
    input_list: list
        Lista dei sintomi inseriti dall'utente
    """

    input_list = []
    print("Insert at least one symptom. Press Enter when you're done.")
    stop = False

    while not stop:
        sym = input()
        
        if not sym and not len(input_list):
            print("Insert at least one symptom to continue.")
        elif not sym:
            stop = True
        elif database.ifValueExists(conn, "criteria", "name", sym):
            input_list.append(sym.lower())
        else:
            print("Symptom not found.")

    return input_list

def mergeList(listOfLists):
    """
    Funzione per unire piú liste in una sola

    Parameters
    ----------
    listOfLists: list
        Lista di liste
    
    Returns
    -------
    mergedList: list
        Unione delle liste in input
    """

    mergedList = []
    for i in range (0, len(listOfLists)):
        for j in range (0, len(listOfLists[i])):
            mergedList.append(listOfLists[i][j][0])   

    return mergedList

def getPercList(list):
    """
    Funzione che calcola la percentuale delle occorenze in una lista,
    ottenuta dividendo il numero di occorenze per la lunghezza della lista

    Parameters
    ----------
    list: list
        Lista contenente gli elementi

    Returns
    -------
    res: defaultdict
        Dizionario le cui chiavi sono gli elementi della lista, i valori sono le percentuali
    """

    res = defaultdict(dict)
    count = Counter(mergeList(list))
    for x in count:
        res[x] = count[x]/len(list)
    return res

def getDictOccurences(l):
    """
    Funzione che restituisce il numero di occorrenze degli elementi di una lista

    Parameters
    ----------
    l: list
        Lista contenente gli elementi
    
    Returns
    -------
    occDict: dict
         Dizionario le cui chiavi sono gli elementi della lista, i valori sono il numero di occorenze
    """

    occDict = {}
    for i in l:
        if i not in occDict.keys():
            occDict[i] = l.count(i)
    return occDict

def getPercOcc(dictOcc, listLenght):
    """
    Funzione che calcola la percentuale delle occorenze in un dizionario,
    data la lunghezza della lista

    Parameters
    ----------
    dictOcc: dict
        Dizionario le cui chiavi sono gli elementi della lista, i valori sono il numero di occorenze
    listLenght: int
        Lunghezza della lista di partenza
    
    Returns
    -------
    dictOcc: dict
         Dizionario le cui chiavi sono gli elementi della lista, i valori sono le percentuali
    
    """

    for i in dictOcc.keys():
        dictOcc[i] = dictOcc[i] / listLenght
    return dictOcc

def tabulateData(conn, predDiag):
    """
    Funzione che organizza i dati in forma tabulare

    Parameters
    ----------
    conn: connection
        Connessione al database
    predDiag:
        Dizionario le cui chiavi sono le diagnosi, i valori sono le probabilità (in percentuale)
    Returns
    -------
    df: DataFrame
         Dati organizzati in forma tabulare, le cui colonne sono il codice della diagnosi,
         il rispettivo nome e percentuale
    """

    names = []
    perc = []
    for k in predDiag:
        names.append(database.getNameFromID(conn, "diagnosis", k))
        perc.append(str(predDiag[k]) + "%")
    data = {"code" : predDiag.keys(), "name" :  names, "probability": perc}
    df = pd.DataFrame(data)
    return df

def main():

    # Connessione e creazione del database
    conn = database.mySQLConnect('localhost', 'root' , "db@1D962")
    if not database.checkIfDbExists(conn, "mentaldisorder"):
        database.createDatabase(conn, "mentaldisorder")
        database.createTablefromFile("datasets/Diagnosis.csv", "diagnosis", conn)
        database.createTablefromFile("datasets/Criteria.csv", "criteria", conn)
        database.createTablefromFile("datasets/CritToDiag.csv", "crit2diag", conn)
    else:
        database.useDatabase(conn, "mentaldisorder")

    # Input dei sintomi
    sym_list = inputSymptoms(conn)

    # Preprocessing
    diag = database.selectJoinID(conn, sym_list, "criteria", "crit2diag", "crit_id", "diag_id") # lista delle diagnosi correlate ai sintomi in input
    mergedList = mergeList(diag)
    categories = database.getValuesCategory(conn, "criteria", sym_list) # categorie dei sintomi in input
    probDiag = getPercList(categories) # percentuale delle categorie in input
    condProbDiag = BBN.getDiagProb(mergeList(categories)) # probabilità delle diagnosi condizionate dai sintomi
    weightProb = BBN.getWeightProb(probDiag, condProbDiag) # calcolo probabilità pesate
    occurences = getDictOccurences(mergedList) # occorrenze delle diagnosi correlate ai sintomi in input
    percDiag = getPercOcc(occurences, len(mergedList)) # percentuale delle occorrenze
    # Prediction
    finalProbCat = BBN.getFinalProbCat(weightProb) # probabilità totale (somma delle probabiltà pesate) delle diagnosi della stessa categoria
    percDiag = BBN.predictDiag(conn, finalProbCat, percDiag) # probabilità della diagnosi
    # Output dei risultati
    print(tabulateData(conn, percDiag))

    # Scelta da parte dell'utente di avere piú info su una diagnosi tramite la lettura di una KB in formato xml
    print("\nIf you would like to have more information about a specific disorder, type the ICD code (Fxx), otherwhise press enter to terminate.")
    stop = False
    while not stop:
        choise = input("Input: ")
        if choise:
            xml.getDiagInfo("datasets/icd-f-section.xml", choise.upper())
        else:
            stop = True


if __name__ == "__main__":
    main()