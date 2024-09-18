import regex as re
import utils
import sys
import os
from smart_open import open
#from normalize import clean
import glob

dir_in ="/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/Brown/"
dir_out = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/Brown/"
target_file = "brown_clean.txt"
text_original = ""
text_cleaned = ""
n_files = 0
utils.profiling_init(utils)
print("\n===CHILDES data processing===\nOpening files in '" + dir_in + "':")

def preprocess(line):
    line = ' '.join(line.strip().split())
    line = line[6:]
    # line = line.lower() # lowercasing
    line = re.sub(r'\[\+ \w+?\]', '', line)  # handling [+ imit] [+ res] [+ imp]
    line = re.sub(r"\S+ \s*\[:\s*(.+?)\]\s*(\[\*.*?\])?", r'\1 ', line)  # [: of] [* fill] [: beat] [* +ed]
    line = re.sub(r"\[\*( .*)?\]", '', line)  # handling [*]

    # Batas [=!  ] [=?  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # handling arrrrr@o [=! wolf noises]
    line = re.sub(r'\S+?\s*\[=\?\s(.+?)\]', r'\1', line)  # handling two months [=? too much]
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # handling [% ] or 0 [%  ]
    # Batas [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # handling 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # handling mhm [= yes]
    line = re.sub(r"\[=\s.+?\]", '', line)  # handling don't say me that [= don't say that I hafta put on my socks]

    # Batas Ampresand &
    line = re.sub(r'&=0', '', line)  # handling &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line)

    line = re.sub(r'„', ',', line)  # replace „ with ,
    line = re.sub(r'\+\<|\+\^|\^', '', line)  # delete +< and +^ and ^
    line = re.sub(r'\+\.\.\.', '[incomplete speech]', line)  # handling +...
    line = re.sub('↫.*?↫', '', line)
    line = re.sub(r'\(\.+\)', ' [PAUSE] ', line)  # handling (.) (..) (...)
    line = re.sub(r'\(|\)', '', line)  # handling op(en)
    line = re.sub(r':', '', line)  # handling mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # handling teddy_bear
    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # handling xxx
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # handling www
    line = utils.normalize_quotes(line)  # normalize quotation

    line = re.sub(r'<.*?>\s*\[/+\](\s*\(\.+\))?|(?:(?!<[^>]*>).)+\[/+\](\s*\(\.+\))?', '',
                  line)  # handling retracing and repetition < > [//] (.)
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # handling [?] [!] [!!]
    line = re.sub(r'<(.*?)>', r'\1', line)  # handling < >
    line = re.sub(r'0', '', line)  # handling 0
    line = re.sub(r'\[<\]|\[>\]', '', line)  # handling [<] and [>]
    line = re.sub(r'[<>]', '', line)  # handling < >

    line = re.sub(r'^[ .?!]*$', '', line)  # handling line with only space . ? !

    line = line.strip(' ')  # handling leading and trailing space
    line = utils.remove_multiple_spacing(line)  # handling multiple spaces
    return line + "\n"


for dirpath, dirnames, filenames in os.walk(dir_in):
    for filename in filenames:
        if filename.endswith('.cha'):  # Only process .cha files
            file_path = os.path.join(dirpath, filename)
            print(".", end="")
            n_files += 1
            with open(file_path, encoding='utf8', errors='ignore') as f:
                for line in f:
                    prev_line = ""
                    prev_cleaned_line = ""

                    if line.startswith("*CHI"):
                        text_original += line
                        cleaned_line = preprocess(line)

                        # Check for duplicate and empty lines in cleaned text
                        if prev_cleaned_line != cleaned_line and not utils.is_empty_line(cleaned_line):
                            prev_cleaned_line = cleaned_line
                            text_cleaned += cleaned_line

# print("\n"+text_cleaned)

utils.report(n_files, text_original, text_cleaned)
utils.save(dir_out, target_file, text_original, text_cleaned)
utils.profiling_end(utils)