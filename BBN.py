import math
import pomegranate as pg
import pandas as pd
import database
import mysql.connector

def getDiagProb(symCatList):
    """
    Funzione che riceve in input la lista delle categorie dei sintomi inseriti dall'utente,
    e tramite l'uso di una Bayesian Belief Network viene calcolata la probabiltà della categoria
    di una diagnosi condizionata dalla categoria dei sintomi, infine restituita sotto forma di lista

    Parameters
    ----------
    symCatList: list
        Lista contenente le categorie dei rispettivi sintomi forniti in input 
    
    Returns
    -------
    condProbs: list
        Lista contenente delle tuple, ogni tupla contiene la categoria e la
        corrispondente probabilità di diagnosi
    """

    data = pd.read_csv("datasets/Criteria.csv")

    criteria = pg.DiscreteDistribution.from_samples(pd.read_csv("datasets/Criteria.csv")["category"])
    diagnosis = pg.ConditionalProbabilityTable(
        [ ['a', 'a', 0.85], ['a', 'b', 0.25], ['a', 'c', 0.2], ['a', 'd', 0.3], ['a', 'e', 0.3], ['a', 'f', 0.3], ['a', 'g', 0.4], ['a', 'h', 0.3], ['a', 'i', 0.2], ['a', 'j', 0.25],
          ['b', 'a', 0.25], ['b', 'b', 0.85], ['b', 'c', 0.1], ['b', 'd', 0.3], ['b', 'e', 0.3], ['b', 'f', 0.2], ['b', 'g', 0.1], ['b', 'h', 0.05], ['b', 'i', 0.05], ['b', 'j', 0.15],
          ['c', 'a', 0.25], ['c', 'b', 0.25], ['c', 'c', 0.85], ['c', 'd', 0.4], ['c', 'e', 0.15], ['c', 'f', 0.4], ['c', 'g', 0.25], ['c', 'h', 0.1], ['c', 'i', 0.15], ['c', 'j', 0.1],
          ['d', 'a', 0.4], ['d', 'b', 0.2], ['d', 'c', 0.3], ['d', 'd', 0.85], ['d', 'e', 0.2], ['d', 'f', 0.1], ['d', 'g', 0.3], ['d', 'h', 0.2], ['d', 'i', 0.15], ['d', 'j', 0.15],
          ['e', 'a', 0.15], ['e', 'b', 0.15], ['e', 'c', 0.15], ['e', 'd', 0.15], ['e', 'e', 0.85], ['e', 'f', 0.25], ['e', 'g', 0.15], ['e', 'h', 0.1], ['e', 'i', 0.1], ['e', 'j', 0.1],
          ['f', 'a', 0.4], ['f', 'b', 0.1], ['f', 'c', 0.2], ['f', 'd', 0.15], ['f', 'e', 0.1], ['f', 'f', 0.85], ['f', 'g', 0.15], ['f', 'h', 0.1], ['f', 'i', 0.1], ['f', 'j', 0.1],
          ['g', 'a', 0.2], ['g', 'b', 0.1], ['g', 'c', 0.1], ['g', 'd', 0.3], ['g', 'e', 0.2], ['g', 'f', 0.15], ['g', 'g', 0.85], ['g', 'h', 0.05], ['g', 'i', 0.05], ['g', 'j', 0.05],
          ['h', 'a', 0.15], ['h', 'b', 0.05], ['h', 'c', 0.05], ['h', 'd', 0.05], ['h', 'e', 0.05], ['h', 'f', 0.05], ['h', 'g', 0.05], ['h', 'h', 0.85], ['h', 'i', 0.05], ['h', 'j', 0.05],
          ['i', 'a', 0.15], ['i', 'b', 0.05], ['i', 'c', 0.05], ['i', 'd', 0.05], ['i', 'e', 0.05], ['i', 'f', 0.05], ['i', 'g', 0.05], ['i', 'h', 0.05], ['i', 'i', 0.85], ['i', 'j', 0.05],
          ['j', 'a', 0.15], ['j', 'b', 0.05], ['j', 'c', 0.05], ['j', 'd', 0.05], ['j', 'e', 0.05], ['j', 'f', 0.05], ['j', 'g', 0.05], ['j', 'h', 0.05], ['j', 'i', 0.05], ['j', 'j', 0.85]], [criteria])

    s1 = pg.State(criteria, name = "criteria")
    s2 = pg.State(diagnosis, name = "diagnosis")
    
    model = pg.BayesianNetwork("Mental disorders diagnostic")
    model.add_states(s1, s2)
    model.add_edge(s1, s2)
    model.bake()

    condProbs = []

    for s in symCatList:
        beliefs = model.predict_proba({'criteria' : s})
        condProbs.append(beliefs[1].parameters[0])
    
    return condProbs   

def getWeightProb(list1, list2):
    """
    Funzione che prende in input una lista con le percentuali delle categorie dei sintomi
    e una lista con le probabilità delle diagnosi. Restituisce una lista con le probabilità
    pesate delle diagnosi, ottenute moltiplicando ogni probabilità delle categorie dei sintomi
    con le corrispettive delle diagnosi

    Parameters
    ----------
    list1: list
        Lista contenente le percentuali per ciascuna categoria di sintomi
    list2: list
        Lista contenente le percentuali per ciascuna categoria di diagnosi
    Returns
    -------
    res: list
        Lista contenenti le probabilità pesate delle diagnosi
    """
    res = []
    for l in list2:
        for k in list1:
            l[k] = l[k] * list1[k]
        res.append(l)
    return res

def getFinalProbCat(list):
    """
    Funzione che effettua la somma di tutte le probabilità della stessa categoria
    all'interno della lista in input, restituendo una lista contenenti le probabilità
    finali

    Parameters
    ----------
    list: list
        lista contenente le probabilità pesate delle diagnosi

    Returns
    -------
    res: list
        lista contenente le probabiltà finali per ciascuna categoria di diagnosi
    """

    res = list.pop(0)
    for k in res:
        for i in list:
            res[k] = res[k] + i[k]
    return res

def predictDiag(conn, probCat, percOcc):
    """
    Funzione che calcola le probabilità di ciascuna diagnosi, il cui risultato
    è un dizionario con diagnosi e rispettiva percentuale

    Parameters
    ----------
    conn: connection
        Connessione al database
    probCat: list
        Lista contenente le probabilità che la diagnosi appartenga ad una categoria
    percOcc: dict
        Dizionario contenente per ciascuna diagnosi le probabilità che l'utente abbia una
        specifica diagnosi
    Returns
    -------
    pred: dict
        Dizionario le cui chiavi sono i codici delle diagnosi e i valori sono le
        probabilità pesate di ogni diagnosi, sotto forma di percentuale
    """

    pred = {}
    
    for k in percOcc.keys():
        category = database.getValueCategory(conn, "diagnosis", str(k))
        pred[k] = percOcc[k] * probCat[category[0]]

    corr = (1 - sum(pred.values())) / len(pred) # correction value
    for k in percOcc.keys():
        pred[k] += corr
        pred[k] = round(pred[k] * 100, 4)

    return pred
   
