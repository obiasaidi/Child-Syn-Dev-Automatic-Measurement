import regex as re
import utils
import sys
import os
from smart_open import open
from normalize import clean
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
    line = ' '.join(line.strip().split()) # Remove extra spaces
    line = line[6:] # Remove the first 6 characters
    line = line.lower() # Convert text to lowercase

    # Handle patterns with [+  ] or [*  ]
    line = re.sub(r'\[\+ \w+?\]', '', line)  # Remove patterns like [+ imit] [+ res] [+ imp]
    line = re.sub(r"\S+ \s*\[:\s*(.+?)\]\s*(\[\*.*?\])?", r'\1 ', line)  # Handle patterns like [: of] [* fill] and [: beat] [* +ed]
    line = re.sub(r"\[\*( .*)?\]", '', line)  # Remove patterns like [*] and [* +s]

    # Handle patterns with [=?  ] [=!  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # Remove patterns like [=! wolf noises]
    line = re.sub(r'\S+?\s*\[=\?\s(.+?)\]', r'\1', line)  # Replace patterns like [=? too much]
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # Remove patterns like [% ] or 0 [%  ]
    
    # Handle [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # Remove patterns like 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # Handle patterns like [= yes]
    line = re.sub(r"\[=\s.+?\]", '', line)  # Handle patterns like don't say me that [= don't say that I hafta put on my socks]

    # Handle Ampersand &
    line = re.sub(r'&=0', '', line)  # Remove patterns like &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line) # Remove patterns like &* &= &~ &+ &-

    line = re.sub(r'„', ',', line)  # Replace „ with ,
    line = re.sub(r'\+\<|\+\^|\^', '', line)  # Remove +< and +^ and ^
    line = re.sub(r'\+\.\.\.', '[incomplete speech]', line)  # Replace +... with [incomplete speech]
    line = re.sub('↫.*?↫', '', line) # Remove text between '↫' symbols
    line = re.sub(r'\(\.+\)', '[PAUSE]', line)  # Replace (.) (..) (...) with [PAUSE]
    line = re.sub(r'\(|\)', '', line)  # Revise patterns like op(en) to be open
    line = re.sub(r':', '', line)  # Remove : in patterns like mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # Remove _ in patterns like teddy_bear
    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # Replace xxx or yyy with [unintellegible speech]
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # Replace www with [untranscribed material]
    line = utils.normalize_quotes(line)  # normalize quotation

    line = re.sub(r'<.*?>\s*\[/+\](\s*\(\.+\))?|(?:(?!<[^>]*>).)+\[/+\](\s*\(\.+\))?', '', line)  # Handle retracing and repetition < > [/] [//] (.)
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # Remove [?] [!] [!!]
    line = re.sub(r'<(.*?)>', r'\1', line)  # Persist text inside < >
    line = re.sub(r'0', '', line)  # Remove 0
    line = re.sub(r'\[<\]|\[>\]', '', line)  # Remove [<] and [>]
    line = re.sub(r'[<>]', '', line)  # Remove unnecessary/left < >

    line = re.sub(r'^[ .?!]*$', '', line)  # Remove space .?! in the lines with only space . ? !

    line = line.strip(' ')  # Remove leading and trailing space
    line = utils.remove_multiple_spacing(line)  # Handle multiple spaces
    return line + "\n"

for dirpath, dirnames, filenames in os.walk(dir_in):
    for filename in filenames:
        if filename.endswith('.cha'):  # Only process .cha files
            file_path = os.path.join(dirpath, filename)
            print(".", end="")
            n_files += 1
            with open(file_path, encoding='utf8', errors='ignore') as f: # errors='ignore' used bcs byte (0xf7) found
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

utils.report(n_files, text_original, text_cleaned)
utils.save(dir_out, target_file, text_original, text_cleaned)
utils.profiling_end(utils)
