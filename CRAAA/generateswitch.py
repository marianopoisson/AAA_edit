import csv
import re

def latexify_accented_characters(input_string):
    """Replace accented characters with LaTeX equivalents."""
    replacements = {
        '\u00e4': '\\"a',  # ä
        '\u00e9': "\\'e",  # é
        '\u00e8': "\\`e",  # è
        '\u00eb': '\\"e',  # ë
        '\u00f3': "\\'o",  # ó
        '\u00f2': "\\`o",  # ò
        '\u00f6': '\\"o',  # ö
        '\u00f4': '\\^o',  # ô
        '\u00f8': '\\o ',  # ø
        '\u00f1': '\\~n',  # ñ
        '\u00ee': '\\^{\\i}',  # î
        '\u00fc': '\\"u',  # ü
        '\\': '\\textbackslash{}'
    }
    for key, value in replacements.items():
        input_string = input_string.replace(key, value)
    return input_string

def parse_input_line(input_line, field_separator=','):
    """Parse a line of input into a dictionary with named fields."""
    input_line = input_line.replace("'", "\\'")
    word_list = next(csv.reader([input_line], delimiter=field_separator))
    word_list = [latexify_accented_characters(word) for word in word_list]
    fields = {
        'type': word_list[0],
        'number': word_list[1],
        'pcdecision': word_list[2],
        'nbpages': word_list[3],
        'title': word_list[4],
        'filename': word_list[5],
        'generatedfrom': word_list[6],
        'cite': word_list[7],
        'authors': [word_list[i:i+2] for i in range(8, len(word_list), 2)]
    }
    return fields

def authors_by_first_name(authors):
    """Return authors as 'First Last'."""
    return [f"{first} {last}" for first, last in authors]

def authors_by_surname(authors):
    """Return authors as 'Last, First'."""
    return [f"{last}, {first}" for first, last in authors]

def gen_index(authors_by_surname):
    """Generate LaTeX index entries for authors."""
    return ''.join([f"\\index{{{author}}}" for author in authors_by_surname])

def gen_bookmark(authors_by_first_name):
    """Generate LaTeX bookmarks for authors."""
    return ''.join([f"\\pdfbookmark[2]{{{author}}}{{#2.{author}}}" for author in authors_by_first_name])

def output_day_latex(fields):
    """Output LaTeX for a day."""
    with open('exsessions.tex', 'a') as sessions_file:
        session_title = fields['title']
        sessions_file.write('\n%%%== Day\n')
        sessions_file.write(f'\\procday{{{session_title}}}\n')

def output_session_latex(fields):
    """Output LaTeX for a session."""
    with open('exsessions.tex', 'a') as sessions_file:
        session_title = fields['title']
        sessions_file.write('\n%%%-- session\n')
        sessions_file.write(f'\\session{{{session_title}}}\n')

def output_paper_latex(fields):
    """Output LaTeX for a paper."""
    with open('expapersswitch.tex', 'a') as swi_file:
        authors_first = authors_by_first_name(fields['authors'])
        authors_surname = authors_by_surname(fields['authors'])
        swi_file.write(f'%======= PAPER ID = {fields["number"]} =======\n')
        swi_file.write(f'\\ifnum\\paperswitch={fields["number"]}\n')
        swi_file.write(f'  \\procpaper[xshift=\\LaTeXxShift{{}}, yshift=\\LaTeXyShift{{}}, npages={fields["nbpages"]}, switch=\\paperswitch,%\n')
        swi_file.write(f'    title={{{fields["title"]}}},% paper title\n')
        swi_file.write(f'    author={{{", ".join(authors_first)}}},% list of authors\n')
        swi_file.write(f'    index={{{gen_index(authors_surname)}}},% authors index entries\n')
        swi_file.write(f'    cite={{{fields["cite"]}}},% cited bib items\n')
        swi_file.write(f'    bookmark={{{gen_bookmark(authors_first)}}}% for PDF bookmark structure\n')
        swi_file.write(f'  ]{{#2}}\n')
        swi_file.write('\\fi\n\n')
        
    with open('exsessions.tex', 'a') as sessions_file:
        sessions_file.write(f'\\paperid{{{fields["number"]}}}{{{fields["filename"]}}}\n')

def main(input_file):
    """Main function to process the input file and generate LaTeX files."""
    with open('expapersswitch.tex', 'w') as swi_file, open('exsessions.tex', 'w') as sessions_file:
        swi_file.write('\\newcommand{\\paperid}[2]{\n\n\\renewcommand{\\paperswitch}{#1}\n\n')

    with open(input_file, 'r') as file:
        for line in file:
            fields = parse_input_line(line.strip())
            if fields['type'].lower() == 'day':
                output_day_latex(fields)
            elif fields['type'].lower() in {'session', 'paper session', 'demo session', 'poster session'}:
                output_session_latex(fields)
            elif fields['type'].lower() in {'oral', 'paper', 'demo', 'poster'}:
                output_paper_latex(fields)
            else:
                print(f'!!! a day, session or paper ({fields["type"]}) is lost by the script...')

    with open('expapersswitch.tex', 'a') as swi_file:
        swi_file.write('}\n')

if __name__ == "__main__":
    input_file = 'exprogram.csv'  # Replace with the actual input file name
    main(input_file)
