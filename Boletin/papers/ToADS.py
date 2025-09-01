#!/usr/bin/env python3
import os
#import hunspell
from termcolor import colored
import numpy as np
import PyPDF2
from shutil import copyfile,rmtree
import pandas as pd
from utils import output_register, create_db, to_ADS, load_acceptedKeywords

################
### SETTINGS ###
################
metadata = {
   # BIBCODE
   # YYYYJJJJJVVVVMPPPPA
  'root_name': '2024BAAA...65',
  'journal_base': 'Boletín de la Asociación Argentina de Astronomía, vol. 65',
  'url_base': 'http://www.astronomiaargentina.org.ar/b65/',
  'pub_date': '08/2024'
}


############
### MAIN ###
############
if __name__ == '__main__':

  lista = np.genfromtxt("ordered_list.txt",dtype=str)

  keywordList = load_acceptedKeywords(filename="newKeys.txt")

  db = create_db(lista,keywordList,getRefs=True)

  to_file = lambda s : "%s/%s.tex" % (s,s)
  db["filename"] = pd.Series(db.index,index=db.index).apply(to_file)
  db["link"] = np.nan
  db["firstpage"] = np.nan
  db["lastpage"] = np.nan

  f = open('PAGEMAP','w')

  pages = 1
  for i in lista:
      inicial = db.loc[i].author['surname_000'][0]
      _pages = f'{pages :.>5}'
      db.loc[i,'link'] = metadata['root_name'] + _pages + '%1s'%inicial + '.pdf'
      db.loc[i,'firstpage'] = pages
      db.loc[i,'lastpage'] = pages + db.loc[i,'npages'] - 1
  
      keys = ''
      for k in db.loc[i,'keywords'].values():
        if k:
          keys += k + ' --- '
      db.loc[i,'keywords'] = keys[:-5]


      _text = "%s %d-%d\n" % (db.loc[i,'link'],db.loc[i,'firstpage'],db.loc[i,'lastpage'])
      f.write(_text)
      pages += db.loc[i,'npages']
      copyfile(db.loc[i,'filename'].replace('.tex','.pdf'),db.loc[i,'link'])
  f.close()

  db.to_parquet('db.parquet',compression='GZIP')

  filename = 'ToADS.txt'
  to_ADS(filename,db,metadata)
  

