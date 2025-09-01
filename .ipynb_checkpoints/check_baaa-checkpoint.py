import checkBAAA
import glob


import os, sys, tarfile

def extract(tar_url, extract_path='./TGZs-iniciales/extracted/'):
    print(tar_url)
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])


lista=[]
for st in glob.glob('./TGZs-iniciales/*.tgz'):
    lista.append(st[17:20])

print('Lista de Articulos analizados por ID: ',lista)


#recover cites from text and bib

def RecoverCites(text, bib=None):
    cites=[]
    for i in text:
        x=i.find("\\cite")
        if x >=0:
            cites.append(i)
    ref=[]
    for c in cites:
        start = 0
        
        while start>=0:
            start = c.find("\\cite", start)
            if start ==-1:
                continue
            j=c[start:].find("{")
            k=c[start:].find("}")
            ref.append(c[start+j+1:start+k])
            start += 5   

    ref0=[]
    for i in ref:
        x=i.split(',')
        for h in x:
            ref0.append(h.replace(' ',''))
    
    ref=ref0
    
    bib=glob.glob(bib)
    f = open(bib[0],'r',encoding=encoding)
    bibtex = f.read().split('@')
    f.close()
    
    
    dcites=[]

    for i in ref:
        j=0
        for c in bibtex:
            j=j+1
            x=c.find(i)
            if x >0:
                dcites.append(j)
    print('# de citas: ',len(set(dcites)))
    
    for p,d in enumerate(set(dcites)):
        bb=bibtex[d-1].split('\n')
        y=bibtex[d-1].find('year')
        x=bibtex[d-1].find('thor')
        startau=bibtex[d-1].find('=',x)
        endau=bibtex[d-1].find(',',x)
        
        starty=bibtex[d-1].find('=',y)
        endy=bibtex[d-1].find(',',y)
    
        print(p+1,bibtex[d-1][startau+1:endau],'...,',bibtex[d-1][starty+1:endy])

for name in lista:

    old_stdout = sys.stdout

    log_file = open('./TGZs-iniciales/'+name+'.log',"w", encoding="utf-8")

    sys.stdout = log_file
    extract(glob.glob('./TGZs-iniciales/'+name+'*.tgz')[0])
    tex=glob.glob('./TGZs-iniciales/extracted/'+name+'.tex')
    bib=glob.glob('./TGZs-iniciales/extracted/*.bib')
    bibf = open(bib[0])
    bibtex = bibf.read()
    bibf.close()

    
    if len(tex) >1 :
        print('multiple tex')
    if len(tex) ==0:
        print('no tex found')
   # sys.argv[1]=tex
    exec(open("checkBAAA.py").read() {tex[0]})
    RecoverCites(text,bib=bib[0])
    files = glob.glob('./TGZs-iniciales/extracted/*')
    for f in files:
        os.remove(f)

    sys.stdout = old_stdout

    log_file.close()