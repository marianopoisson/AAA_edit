import os
import csv
from pylatexenc.latexencode import unicode_to_latex

# Función para extraer el título de un archivo .tex
def extract_title(tex_file):
    with open(tex_file, 'r',encoding='utf-8') as file:
        for line in file:
            if '\\title{' in line:
                return line.split('{')[1].split('}')[0]
    return 'Unknown Title'

'''
def extract_authors(tex_file):
    #print(colored('*****Checking Authors',"green"))
    # Solo revisa que no haya espacios entre las iniciales del nombre, y que los apellidos compuestos sean correctos.
    f=open(tex_file, 'r',encoding='utf-8')
    text = f.readlines()
    f.close()
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
      print(' bad last-author separator: \\&')

    authors = {}
    for i,t in enumerate(text):
        j = t.rfind('.')

        name = t[:j+1].strip()
        name = name.replace('\n','')
        name = name.replace('\\','')
        if ' ' in name:
          print(' bad author: %s' % (name))

        if not isascii(name):
          name = unicode_to_latex(name,non_ascii_only=True)

        surname = t[j+1:].strip()
        surname = surname.replace('\n','')

        if ' ' in surname:
          print(" Check apellido -> %s" % (surname))

        if not isascii(surname):
          surname = unicode_to_latex(surname,non_ascii_only=True)

        col = 'name_%03d' % i
        authors[col] = unicode_to_latex(name,non_ascii_only=True)
        col = 'surname_%03d' % i
        authors[col] = unicode_to_latex(surname,non_ascii_only=True)

    #print(colored('PASSED',"green"))
    return(list(authors.values()))
'''
# Función para extraer autores de un archivo .tex
def extract_authors(tex_file):
    authors = []
    with open(tex_file, 'r',encoding='utf-8') as file:
        for line in file:
            if '\\author{' in line:
                author_line = line.split('{')[1].split('}')[0].replace('\\&',',')
                while True:
                    try:
                        i = author_line.index('\\inst{')
                        abierto = 1
                        k = i + 7
                        while abierto > 0:
                            if author_line[k] == '{':
                                abierto += 1
                            if author_line[k] == '}':
                                abierto -= 1
                            k += 1
                            author_line = author_line[:i] + author_line[k:]
                    except ValueError:
                        break
                authors = [author.strip() for author in author_line.split(',')]
                break
    return authors



# Función para extraer citas de un archivo .bib
def extract_citations(bib_file):
    citations = []
    with open(bib_file, 'r') as file:
        for line in file:
            if line.startswith('@'):
                citation = line.split('{')[1].split(',')[0]
                citations.append(citation)
    return citations

# Función para extraer el área temática de un archivo .tex
def extract_thematic_area(tex_file):
    with open(tex_file, 'r',encoding='utf-8') as file:
        for line in file:
            if '\\thematicarea{' in line:
                return line.split('{')[1].split('}')[0]
    return 'Unknown Area'

# Directorio raíz donde se encuentran los subdirectorios con los archivos .tex y .bib
root_dir = "../papers/"  # Cambia esto por el directorio correspondiente

# Archivo de salida
output_file = 'inputfile.csv'

# Lista para almacenar los datos extraídos
data = []

# Recorrer todos los subdirectorios en el directorio raíz
for subdir in os.listdir(root_dir):
    print(subdir)
    subdir_path = os.path.join(root_dir, subdir)
    if os.path.isdir(subdir_path) and subdir.isdigit():
        tex_file = os.path.join(subdir_path, f'{subdir}.tex')
       # bib_file = os.path.join(subdir_path, f'*.bib')

        if os.path.isfile(tex_file):
            title = extract_title(tex_file)
            authors = extract_authors(tex_file)
           # citations = extract_citations(bib_file)
            thematic_area = extract_thematic_area(tex_file)

          #  author_pairs = [(authors[i], authors[i+1]) for i in range(0, len(authors), 2)]

            data.append([
                'paper',  # type
                subdir,  # number
                '',  # pcdecision
                '',  # nbpages (puedes ajustar esto si tienes esa información)
                title,  # title
         #       f'{subdir}.pdf',  # filename
         #       'generatedfrom',  # generatedfrom
        #        ','.join(citations) if citations else '',  # cite
                thematic_area,  # thematic area
                *authors
             #   *list(sum(author_pairs, ()))  # flatten the list of author pairs
            ])

# Escribir los datos en el archivo de salida
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in data:
        writer.writerow(row)

print(f'Datos guardados en {output_file}')
