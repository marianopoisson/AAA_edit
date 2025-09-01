#!/usr/bin/env python3
import os
#import hunspell
from termcolor import colored
import numpy as np
import PyPDF2
import pandas as pd
from utils import load_acceptedKeywords, create_db, write_sessions, write_expapersswitch

############
### MAIN ###
############

if __name__ == '__main__':

  #keywordList = load_acceptedKeywords(filename="acceptedKeywords.txt")
  keywordList = load_acceptedKeywords(filename="newKeys.txt")

  lista = np.genfromtxt("listaall.txt",dtype=str)

  db = create_db(lista,keywordList)

  #db.to_parquet('db.parquet',compression='GZIP')
  db.to_csv('lala.txt',index=True)
  
  authors = db['author'].apply(pd.Series)

  df = pd.DataFrame(columns=["type","ID","contrib",
                             "Npages","title","filename",
                             "generated","citations"],index=db.index)

  df["Npages"] = db["npages"]
  df["type"] = "paper"
  df["ID"] = db.index
  df["title"] = db["title"]
  df["generated"] = "LaTeX"
  df["contrib"] = "R"

  to_file = lambda s : "%s/%s.tex" % (s,s)
  df["filename"] = df["ID"].apply(to_file)
  
  df = df.join(authors)
  df.to_csv('to_papers.csv',sep=';',index=False)

  write_sessions(db)
  df['contribtype'] = db['contribtype']
  write_expapersswitch(df)


#  if(m['contriblanguage'] == '0'):
#    diccionario = hunspell.HunSpell('/usr/share/hunspell/es_AR.dic', 
#                                    '/usr/share/hunspell/es_AR.aff')
#
#  palabras_aleatorias = []
#  print('Se corrigieron las siguientes palabras: ')
#  print(corregir_palabras(diccionario, m['title'],))
#
#  print(m)
