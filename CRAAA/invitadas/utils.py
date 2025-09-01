#!/usr/bin/env python3
import os
#import hunspell
from termcolor import colored
import numpy as np
import PyPDF2
import pandas as pd
from pylatexenc.latexencode import unicode_to_latex
from chardet.universaldetector import UniversalDetector
import textwrap as tr

language = {'0': 'Spanish',
            '1': 'English'}

contribtype = {'1': 'Presentación mural',
               '2': 'Presentación oral',
               '3': 'Informe invitado',
               '4': 'Mesa redonda',
               '5': 'Presentación Premio Varsavsky',
               '6': 'Presentación Premio Sahade',
               '7': 'Presentación Premio Sérsic'}

thematicarea = {'1':'SH. Sol y Heliosfera',
                '2':'SSE. Sistemas Solar y Extrasolares',
                '3':'AE. Astrofísica Estelar',
                '4':'SE. Sistemas Estelares',
                '5':'MI. Medio Interestelar',
                '6':'EG. Estructura Galáctica',
                '7':'AEC. Astrofísica Extragaláctica y Cosmología',
                '8':'OCPAE. Objetos Compactos y Procesos de Altas Energías',
                '9':'ICSA. Instrumentación y Caracterización de Sitios Astronómicos',
               '10':'AGE. Astrometría y Geodesia Espacial',
               '11':'ASOC. Astronomía y Sociedad',
               '12':'O. Otros'}

def load_acceptedKeywords(filename="acceptedKeywords.txt"): 
  f = open(filename,"r")
  keywordList = f.readlines()
  for i in range(len(keywordList)):
    keywordList[i] =  keywordList[i].replace('\n','')
  f.close()
  return(keywordList)

def return_metadata(text,keys):
  metadata = {}

  while True:
    try:
       i = text.index('\\')
       j = text.index('{', i)
       key = text[i + 1: j]
       k = j + 1
       abierto = 1

       while abierto > 0 and k < len(text):
         if text[k] == '{':
           abierto += 1
         if text[k] == '}':
           abierto -= 1
         k += 1

       if key in keys:
         metadata[key] = text[j + 1: k - 1].strip()

       text = text[k:]
    except ValueError:
       break
    except IndexError:
       break

  for required_key in keys:
    if required_key not in metadata:
      metadata[required_key] = None

  return(metadata)

def clean_abstract(text):
    text = text.replace('\n',' ')

    if '\\\\' in text:
      print(colored('Abstract con salto de linea %s %s' % (os.getcwd(),text),"light_red"))
    text = text.replace('\\\\','')

    text = text.lstrip()
    text = text.rstrip()
    while '  ' in text:
      text = text.replace('  ',' ')

    text = tr.fill(text, width=72)

    return(text)

def clean_title(title,subtitle):
    print(colored('Chequeando title',"light_grey"))
    isascii = lambda s: len(s) == len(s.encode())

    if (subtitle):
      title = title + ' ' + subtitle
      print(colored('  Warning! tiene subtitulo %s ' % title, 'light_red'))

    title = title.replace('\n',' ')
    if '\\\\' in title:
      print(colored('Titulo con salto de linea %s %s' % (os.getcwd(),title),"light_red"))
    title = title.replace('  ',' ')

    title = title.replace('\\\\','')
    if not isascii(title):
      title = unicode_to_latex(title,non_ascii_only=True)
    title = title.lstrip()
    title = title.rstrip()
    while '  ' in title:
      title = title.replace('  ',' ')
    
    print(colored('... passed',"light_grey"))
    return(title)

def clean_keywords(text,keywordList):
    print(colored('Chequeando Keywords',"light_grey"))

    isascii = lambda s: len(s) == len(s.encode())

    if not (' --- ' in text):
      print(colored('  * error separador keywords',"light_red"))
      print('      ',colored(text.split(' --- '),"light_grey"))

    text = text.split(' --- ')

    keywords = {}
    for i,t in enumerate(text):
        key = t
        key = key.replace('\n','')
        key = key.replace('\t','')
        key = key.replace('\\','')
        key = key.strip()

#        _key = False
#        if key.endswith(')'):
#          _key = key
#          i = key.find('(')
#          key = key[:i]
        
        if not isascii(key):
          key = unicode_to_latex(key,non_ascii_only=True)

        if not (key in keywordList):
          print(colored('  bad keyword: %s ' % key,'light_red'))
        
#        if _key:
#          key = _key

        col = 'key_%03d' % i
        keywords[col] = key

    print(colored('... passed',"light_grey"))
    return(keywords)

def clean_refs(text):
    for i,t in enumerate(text):
      t = t.replace('\n','')
      text[i] = t
    if '' in text:
      text.remove('')
    return(text)

def clean_author(text):
    print(colored('Chequeando Authors',"light_grey"))
    isascii = lambda s: len(s) == len(s.encode())

    text = text.replace('\n',' ')
    while '  ' in text:
      text = text.replace('  ',' ')
        
    while '\\\\' in text:
      text = text.replace('\\\\','')

    while True:
      try:
         i = text.index('\\inst{')
         abierto = 1
         k = i + 7
         while abierto > 0:
           if text[k] == '{':
             abierto += 1
           if text[k] == '}':
             abierto -= 1
           k += 1
         text = text[:i] + text[k:]
      except ValueError:
        break

    oneAuthor = False
    if not ('&' in text):
      oneAuthor = True

    text = text.replace('{\&}',',')
    text = text.replace('\&',',').split(',')

    if (len(text) > 1) and oneAuthor:
      print(colored('  * error falta ultimo autor \&',"light_red"))

    authors = {}
    for i,t in enumerate(text):
        j = t.rfind('.')

        name = t[:j+1].strip()
        #name = name.replace('\n','')
        #name = name.replace('\\','')
        if ' ' in name:
          print(colored('Check nommbre %s %s' % (os.getcwd(),name),"light_red"))

        if not isascii(name):
          name = unicode_to_latex(name,non_ascii_only=True)

        surname = t[j+1:].strip()
        surname = surname.replace('\n','')

        if ' ' in surname:
          print(colored("Check apellido %s %s" % (os.getcwd(),surname),"light_red"))

        if not isascii(surname):
          surname = unicode_to_latex(surname,non_ascii_only=True)

        col = 'name_%03d' % i
        authors[col] = name
        col = 'surname_%03d' % i
        authors[col] = surname

    print(colored('... passed',"light_grey"))
    return(authors)

def return_header(text):

  indx = text.index("\\begin{document}\n")
  text = text[:indx]
  
  t = []
  for l in text:
      if l.startswith("%"):
          continue
      t.append(l)
  
  a = []
  for l in t:
      if l == '\n':
          continue
      a.append(l)
  
  b = []
  for l in a:
      if l.startswith('\\documentclass'):
          continue
      b.append(l)
  
  c = []
  for l in b:
      if l.startswith('\\usepackage'):
          continue
      c.append(l)
  
  d = ''
  for i in c:
      d += i
  return(d)

def corregir_palabras(corrector, palabras, agregarPrimero=[]):   
    codificacion = corrector.get_dic_encoding()

    # agregamos las palabras aleatorias al diccionario
    for palabra in agregarPrimero:
        corrector.add(palabra)

    # autocorreccion de palabras
    corregida = []
    for p in palabras:
        ok = corrector.spell(p)   # verificamos ortografia
        if not ok:
            sugerencias = corrector.suggest(p)
            if len(sugerencias) > 0:  # hay sugerencias
                # tomamos la  mejor sugerencia(decodificada a string)
                mejor_sugerencia = sugerencias[0]   
                corregida.append(mejor_sugerencia)
            else:
                corregida.append(p)  # no hay ninguna sugerecia para la palabra
        else:
            corregida.append(p)   # esta palabra esta corregida

    return corregida

def output_register(df,pfout,metadata):

  fpage = df['firstpage'] 
  lpage = df['lastpage'] 
  journal = metadata['journal_base']+", p.%d-%d" % (fpage,lpage) 
  url = metadata['url_base']+df['link'] 
  authors = ""
  for i in range(int(df['num_authors'])//2):
    if i != 0:
      authors += "; "
    surname = df['author']['surname_%03d'%i]
    initials = df['author']['name_%03d'%i]
    initials = initials.replace('.','. ').strip()
    authors += f'{surname}, {initials}'

  refs = ''
  if df['refs'] == df['refs']: #check refs es no nan
    refs = '\n'.join(df['refs'])

  pfout.write("%R "+df['link'].replace('.pdf','')) #ID 2019baaa...61a...35L.pdf
  pfout.write("\n%A "+authors) #Authors
  pfout.write("\n%%P %d"%fpage) #First Page
  pfout.write("\n%%L %d"%lpage) #Last page
  pfout.write("\n%T "+df['title']) #Title
  pfout.write("\n%K "+df['keywords'])   #Keywords
  pfout.write("\n%M "+df['contriblanguage']) #languague 
  pfout.write("\n%D "+metadata['pub_date']) #publication date MM/AAAA
  pfout.write("\n%B "+df['abstract']) #abstract
  pfout.write("\n%Z "+refs) #References one by line 
  pfout.write("\n%I PDF:"+url) #URL
  pfout.write("\n%J "+journal) #Journal BAAA, vol. 62, p.35-37
  pfout.write("\n")
  pfout.write("\n")

def to_ADS(filename,df,metadata):
    f = open(filename,"w")
    for i,row in df.iterrows():
        output_register(row,f,metadata)
    f.close()

def create_db(lista,keywordList,getRefs=False):

  db = {}
  for l in lista:
    print(colored(f"Paper {l}","light_grey",attrs=['bold']))
    m = process(l,keywordList)

    if getRefs:
      f = open(l+'.refs','r')
      refs = f.readlines()
      f.close()
      refs = clean_refs(refs)
      m['refs'] = refs

    db[l] = m

  db = pd.DataFrame(data=db.values(),index=db.keys())
  return(db)

def outputpaperlatex(df,pfout):

  pfout.write('%======= PAPER ID = ' + df['ID'] + ' =======\n')
  pfout.write('\ifnum\paperswitch=' +  df['ID'] + '\n')
  pfout.write('  \procpaper[xshift=\LaTeXxShift{}, yshift=\LaTeXyShift{}, npages=' + '%d'%df['Npages'] + ', switch=\paperswitch,\n')

  special = ['Presentación Premio Sahade',
             'Presentación Premio Varsavsky',
             'Presentación Premio Sérsic',
             'Informe invitado']

  if df['contribtype'] in special:
    title = f'{df["title"]}. \\textbf{{{df["contribtype"]}}}'
  else:
    title = df["title"]
  pfout.write(f'    title={{{title}}},% paper title\n')

  authors = df[8:-1]
  authors = authors[~authors.isna()]
  assert(len(authors)%2 == 0)

  names = authors[::2]
  surnames = authors[1::2]

  a = ''
  for i in range(len(names)):
    if (i > 0):
      if(i < (len(names)-1)):
        a += ', '
      else:
        a += r' \& '
    a += names[i]+' '+surnames[i]

  index = ''
  for i in range(len(names)):
    index += '\\index{'+surnames[i]+', '+names[i]+'}'

  pfout.write(f'    author={{{a}}},% list of authors\n')
  pfout.write(f'    index={{{index}}},% authors index entries\n')
  pfout.write('    cite={ },% cited bib items\n')
  pfout.write('    bookmark={ }% for PDF bookmark structure\n')
  pfout.write('  ]{#2}\n')
  pfout.write('\\fi\n\n')

def write_expapersswitch(df):
  f = open('expapersswitch.tex','w')
  f.write("\\newcommand{\paperid}[2]{\n\n")
  f.write("\\renewcommand{\paperswitch}{#1}\n\n")
  for i in range(df.shape[0]):
    outputpaperlatex(df.iloc[i],f)
  f.write("}\n")
  f.close()

def write_sessions(db):
  order = ['Mesa redonda',
           'SH. Sol y Heliosfera',
           'SSE. Sistemas Solar y Extrasolares',
           'AE. Astrofísica Estelar',
           'SE. Sistemas Estelares',
           'MI. Medio Interestelar',
           'EG. Estructura Galáctica',
           'AEC. Astrofísica Extragaláctica y Cosmología',
           'OCPAE. Objetos Compactos y Procesos de Altas Energías',
           'AGE. Astrometría y Geodesia Espacial',
           'ICSA. Instrumentación y Caracterización de Sitios Astronómicos',
           'ASOC. Astronomía y Sociedad',
           'O. Otros']

  suborder = ['Presentación Premio Sahade',
              'Presentación Premio Sérsic',
              'Informe invitado',
              'Presentación Premio Varsavsky',
              'Presentación oral',
              'Presentación mural']

  f = open("sessions.tex","w")
  s = 0
  for i in order[:1]:
    index = db['contribtype'] == i
    s += sum(index)
    for k in db.index[index]:
      f.write("\n\session{"+i+"}")
      f.write("\n\paperid{%s}{%s/%s}" % (k,k,k))

  for i in order[1:]:
    f.write("\n\session{"+i+"}")
    for j in suborder:
      index = (db['contribtype'] == j) & (db['thematicarea'] == i)
      s += sum(index)
      for k in db.index[index]:
        if j == suborder[0]:
          print('INVITADAAA ',k)
        f.write("\n\paperid{%s}{%s/%s}" % (k,k,k))

  f.close()

  assert(s == db.shape[0])

def extract_references(l):
    # Cambiamos al directorio del artículo
    os.chdir(l)

    # Abrimos el archivo .tex
    with open(l + '.tex', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Buscamos las referencias (entre \begin{thebibliography} y \end{thebibliography})
    start = None
    end = None
    for i, line in enumerate(lines):
        if '\\begin{thebibliography}' in line:
            start = i
        if '\\end{thebibliography}' in line:
            end = i
            break

    if start is not None and end is not None:
        # Extraemos las referencias
        references = lines[start + 1:end]

        # Limpieza básica del texto
        references = [ref.strip() for ref in references if ref.strip()]

        # Escribimos el archivo .refs
        with open(l + '.refs', 'w', encoding='utf-8') as refs_file:
            refs_file.write("\n".join(references))
    
    os.chdir('..')


def process(l,keywordList):
#  os.chdir(l)

  detector = UniversalDetector()                         
  detector.reset()
  for line in open(l+".tex","rb"):                      
    detector.feed(line)
    if detector.done: break
  detector.close()
  encoding = detector.result['encoding']

  f = open(l+'.tex','r',encoding=encoding)
  text = f.readlines()
  f.close()

  keys = ['contriblanguage','contribtype','thematicarea','title','author','abstract','subtitle','keywords']

  d = return_header(text)
  m = return_metadata(d,keys)

  m['title']  = clean_title(m['title'],m['subtitle'])
  m['author']  = clean_author(m['author'])
  m['keywords']  = clean_keywords(m['keywords'],keywordList)
  m['abstract'] = clean_abstract(m['abstract'])
  m['contriblanguage']  = language[m['contriblanguage']]
  m['contribtype'] = contribtype[m['contribtype']]
  m['thematicarea'] = thematicarea[m['thematicarea']]
  m['num_authors'] = len(m['author'])

#  f = open(l+'.pdf', 'rb')
#  fileReader = PyPDF2.PdfReader(f)
  m['npages'] = 1 #len(fileReader.pages)

 # os.chdir('..')

  return(m)
