#!/usr/bin/env python3
import os
import sys
#import hunspell
from termcolor import colored
import numpy as np
import PyPDF2
import pandas as pd
from pylatexenc.latexencode import unicode_to_latex
from pylatexenc.latex2text import LatexNodes2Text
from chardet.universaldetector import UniversalDetector
import difflib
import re

"""

Script to check the editorial style of the CRAAA

Packages: See README

Usage: python3 checkCRAAA.py test_CRAAA.tex

Changes log:
-20201001: First version - Mario Agustin Sgro <observandum@gmail.com> 
-20201007: Updated afiliations file and some cosmetics - franciscoaiglesias@gmail.com
-20201008: it ignores parentheses in keywords list - franciscoaiglesias@gmail.com
-20201019: only prints msg for errors - franciscoaiglesias@gmail.com

"""
#CONSTANTS

afffile="BAAA_affiliations_20211109.txt"

kwrdfile="BAAA_keywords_20201007.txt"

language = {'0': 'Castellano',
            '1': 'English'}

contribtype = {'1': 'Research article',
               '2': 'Invited review',
               '3': 'Round table',
               '4': 'Invited report Varsavsky Prize',
               '5': 'Invited report Sahade Prize',
               '6': 'Invited report Sérsic Prize'
               }

thematicarea = { '1':'SH. Sol y Heliosfera',
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
           
#
isascii = lambda s: len(s) == len(s.encode())

f = open(kwrdfile,"r")
keywordList = f.readlines()
for i in range(len(keywordList)):
  keywordList[i] =  keywordList[i].replace('\n','')
  keywordList[i] =  re.sub("[\\(\\[].*?[\\)\\]]", "", keywordList[i]).strip()
  #casos con () que estan OK
  if  keywordList[i] == 'magnetohydrodynamics': 
     keywordList[i] = 'magnetohydrodynamics (MHD)'
  if  keywordList[i] == 'Sun: coronal mass ejections':
     keywordList[i] = 'Sun: coronal mass ejections (CMEs)'     
f.close()

#f = open(afffile,"r")
#aList = f.readlines()
#for i,text in enumerate(aList):
#  text =  text.replace('\n','')
#  if not isascii(text):
#    text = unicode_to_latex(text,non_ascii_only=True)
#  aList[i] =  text
#f.close()

f = open(afffile,"r")
aList = f.readlines()
for i,text in enumerate(aList):
  text =  text.replace('\n','')
#  if not isascii(text):
 #   text = unicode_to_latex(text,non_ascii_only=True)
  aList[i] =  LatexNodes2Text().latex_to_text(text)
f.close()


def return_metadata(text,keys):
  metadata = dict()
  while True:
    try:
       i = text.index('\\')
       j = text.index('{')
       key = text[i+1:j]
       k = j + 1
       abierto = 1

       while abierto > 0:
         if text[k] == '{':
           abierto += 1
         if text[k] == '}':
           abierto -= 1
         k += 1

       if key in keys:
         metadata[key] = text[j+1:k-1] 

       text = text[k-1:]
    except ValueError:
       break

  if not ('subtitle' in metadata.keys()):
    metadata['subtitle'] = False

  return(metadata)

def clean_keywords(text):
    #print(colored('*****Checking Keywords',"yellow"))

    isascii = lambda s: len(s) == len(s.encode())

    if not (' --- ' in text):
      print(colored('  * error separador keywords',"yellow"))
      return(0)

    text = text.split(' --- ')

    keywords = {}
    for i,t in enumerate(text):
        key = t
        key = key.strip()
        key = key.replace('\n','')
        key = key.replace('\t','')
        key = key.replace('\\','')
        
        if not isascii(key):
          key = unicode_to_latex(key,non_ascii_only=True)

        if not (key in keywordList):
          print(colored('  bad keyword: %s ' % key,'yellow'))
          try:
            sugg =difflib.get_close_matches(r'{}'.format(key), keywordList)[0]
          except:
            sugg = 'NO MATCH'
          print(colored('  suggestion : '+sugg,'yellow'))
          print('')

        col = 'key_%03d' % i
        keywords[col] = key

    #print(colored('PASSED',"yellow"))
    return(keywords)

def clean_affil(text):
    #print(colored('*****Checking Institute',"white"))

    isascii = lambda s: len(s) == len(s.encode())

    text = text.split('\\and')

    affiliations = {}
    for i,t in enumerate(text):
        key = t
        key = key.replace('\n','')
        key = key.replace('\t','')
        key = key.strip()
        
        key = LatexNodes2Text().latex_to_text(key)
#        if not isascii(key):
#          key = unicode_to_latex(key,non_ascii_only=True)

        if not (key in aList):
          print(colored('  check affil : %s ' % key,'white'))
          try:
            sugg =difflib.get_close_matches(r'{}'.format(key), aList)[0]
          except:
            sugg = 'NO MATCH'
          print(colored('  suggestion: '+sugg,'white'))
          print('')

        col = 'key_%03d' % i
        affiliations[col] = key

    #print(colored('PASSED',"white"))
    return(affiliations)


def clean_title(title,subtitle):
    #print(colored('*****Checking Title',"blue"))
    isascii = lambda s: len(s) == len(s.encode())

    if (subtitle):
      title = title + ' ' + subtitle
      title = title.replace('  ',' ')
      print(colored('  Warning! tiene subtitulo %s ' % title, 'blue'))

    title = title.replace('\n','')
    if not isascii(title):
      title = unicode_to_latex(title,non_ascii_only=True)

    #print(colored('PASSED',"blue"))
    return(title)

def clean_author(text):
    #print(colored('*****Checking Authors',"green"))
    # Solo revisa que no haya espacios entre las iniciales del nombre, y que los apellidos compuestos sean correctos.
    isascii = lambda s: len(s) == len(s.encode())

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

    text = text.replace('{\\&}',',')
    text = text.replace('\\&',',').split(',')

    

    if (len(text) > 1) and oneAuthor:
      print(colored(' bad last-author separator: \\&',"green"))

    authors = {}
    for i,t in enumerate(text):
        j = t.rfind('.')

        name = t[:j+1].strip()
        name = name.replace('\n','')
        name = name.replace('\\','')
        if ' ' in name:
          print(colored(' bad author: %s' % (name),"green"))

        if not isascii(name):
          name = unicode_to_latex(name,non_ascii_only=True)

        surname = t[j+1:].strip()
        surname = surname.replace('\n','')

        if ' ' in surname:
          print(colored(" Check apellido -> %s" % (surname),"green"))

        if not isascii(surname):
          surname = unicode_to_latex(surname,non_ascii_only=True)

        col = 'name_%03d' % i
        authors[col] = name
        col = 'surname_%03d' % i
        authors[col] = surname

    #print(colored('PASSED',"green"))
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

if __name__ == '__main__':

    filename = sys.argv[1]
    
    detector = UniversalDetector()                         
    detector.reset()
    for line in open(filename,"rb"):                      
      detector.feed(line)
      if detector.done: break
    detector.close()
    encoding = detector.result['encoding']

    f = open(filename,'r',encoding=encoding)
    text = f.readlines()
    f.close()
 
    keys = ['contriblanguage','contribtype','thematicarea',
            'title','author','abstract','subtitle',
            'keywords','institute']

    d = return_header(text)
    m = return_metadata(d,keys)

    print("*******************************************")
    print("**** CRAAA TEST SCRIPT (File "+os.path.basename(filename)+") ****")
    print("*******************************************")
    m['title']  = clean_title(m['title'],m['subtitle'])
    m['author']  = clean_author(m['author'])
    m['institute']  = clean_affil(m['institute'])
    m['keywords']  = clean_keywords(m['keywords'])
    m['contriblanguage']  = language[m['contriblanguage']]
    m['contribtype'] = contribtype[m['contribtype']]
    m['thematicarea'] = thematicarea[m['thematicarea']]
    m['num_authors'] = len(m['author'])
