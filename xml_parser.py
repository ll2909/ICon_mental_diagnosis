import xml.etree.ElementTree as ET
import numpy as np

def getDiags(file_in, file_out):
    """
    Funzione che legge il file xml in input e salva il codice e il nome delle diagnosi in formato csv

    Parameters
    ----------
    file_in: str
        Nome/percorso del file in input
    file_out: str
        Nome/percorso del file in output 
    """

    #XML ottenuto da https://www.cdc.gov/nchs/icd/icd10cm.htm
    tree = ET.parse(file_in)
    root = tree.getroot()

    codeList = []
    diagList = []

    for section in root:
        diags = section.findall("diag")
        for d in diags:
            codeList.append(d.find("name").text)
            diagList.append(d.find("desc").text)

    diags = np.column_stack((codeList, diagList))
    np.savetxt(file_out, diags, fmt='%s',delimiter=',')

def getDiagInfo(xml, code):
    """
    Funzione che stampa a video tutte le informazioni su una specifica diagnosi
    e le sue sottodiagnosi, con i rispettivi codici

    Parameters
    ----------
    xml: str
        Nome/percorso del file xml
    code: str
        codice/id della diagnosi 
    """

    tree = ET.parse(xml)
    root = tree.getroot()
    found = False

    for section in root:
        for d in section.findall("diag"):
            if d.find("name").text == code:
                found = True
                print("\n", d.find("name").text, ": ", d.find("desc").text, "\n")
                try:
                    print("Inclusion Term:", *[n.text for n in d.find("inclusionTerm").findall("note")], sep = "\n")
                except Exception:
                    pass
                try:
                    print("Includes:", *[n.text for n in d.find("includes").findall("note")], sep = "\n")
                except Exception:
                    pass    
                try:            
                    if d.find("excludes1").findall("note")[0] is not None:
                        print("Excludes (1):")
                        print(*[n.text for n in d.find("excludes1").findall("note")], sep = "\n")
                    if d.find("excludes2").findall("note")[0] is not None:
                        print("Excludes (2):")
                        print(*[n.text for n in d.find("excludes2").findall("note")], sep = "\n")
                except Exception:
                    pass 
                
                if d.findall("diag"):
                    print("\nSubdiagnosis:")
                for sd in d.findall("diag"):
                    print("\n", sd.find("name").text, ": ", sd.find("desc").text)
                    try:
                        print("Inclusion Term:", *[n.text for n in sd.find("inclusionTerm").findall("note")], sep = "\n")
                    except Exception:
                        pass
                    try:
                        if sd.find("excludes1").findall("note")[0] is not None:
                            print("Excludes (1):")
                            print(*[n.text for n in sd.find("excludes1").findall("note")], sep = "\n")
                        if sd.find("excludes2").findall("note")[0] is not None:
                            print("Excludes (2):")
                            print(*[n.text for n in sd.find("excludes2").findall("note")], sep = "\n")
                    except Exception:
                        pass
                        
    if not found:
        print("Not found")
    print("\n")