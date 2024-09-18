import regex as re
import utils
def clean(line):
    line = line[6:]
    line = re.sub(r' \d+_\d+-?', '', line.strip())  # delete digit
    line = re.sub(r'\[- hun\].*[.!?]', '', line)  # handling [- hun]
    line = re.sub(r'\[\+\sdia\]|\[\+\sgram\]', '', line)  # handling [+ dia] [+ gram]
    # Batas [*]
    line = re.sub(r"\[\*\s[mp]\]", '', line)
    line = re.sub(r'[\wʃʌɪɯəɪˈʤʧ@]+\s*\[\*\s(\w{2,})\]', r'\1', line)  # handling [* forgot] [* that]
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*\]', r'\1', line)
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*.+?\]', r'\1', line)
    line = re.sub(r'\[\*\s[^m].+?\]', '', line)
    line = re.sub(r'\S+?\s*\[=\s*(.+?)\]\s*\[\*\]', r'\1', line)
    line = re.sub(r'\S+?\s*\[\*\]\s*\[=\s*(.+?)\]', r'\1', line)
    line = re.sub(r'\[\*\]', '[possible gram error]', line)  # handling [*]
    # Batas [* m: ]
    line = re.sub(r'\[\*\sm:=ed\]', '[past error]', line)  # handling [*m:=ed]
    line = re.sub(r'\s*\[\*\sm:0(\w+).*?\]', r'\1', line)  # handling [m:0 ] missing reg form
    line = re.sub(r'\[\*\sm:a\]', '[morph error]', line)  # handling [*m:a] morph error
    line = re.sub(r"s \[\* m=s\]", '', line)  # handling [* m=s] morph error
    # Batas [=!  ] [=?  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # handling arrrrr@o [=! wolf noises]
    line = re.sub(r'two months \[=\? (too much)\]', r'\1', line)  # handling two months [=? too much]
    line = re.sub(r'\S+?\s*\[=\?\s(.+?)\]', r'\1', line)  # handling two months [=? too much]
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # handling [% ] or 0 [%  ]
    # Batas [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # handling 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # handling mhm [= yes]
    line = re.sub(r"\[=\s.+?\]", '', line)  # handling don't say me that [= don't say that I hafta put on my socks]

    # Batas dat [: that]
    line = re.sub(r"\S+ \[: (.+?)\]", r'\1', line)  # handling dat [: that]

    line = re.sub(r'<.*?>\s*\[/+\]|\S+?(\[>\])?\s\[/+\]', '', line)  # handling [/] [//] retracing

    # Batas
    line = re.sub(r'\+\.{2,3}', '[incomplete speech]', line)  # handling +.. or +...
    line = re.sub(r'\+\+', '', line)  # handling ++
    line = re.sub(r'\(\.+\)', '[PAUSE]', line)  # handling (.) (..) (...)
    line = re.sub(r'\(|\)', '', line)  # handling op(en)
    line = re.sub(r':', '', line)  # handling mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # handling teddy_bear
    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # handling xxx
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # handling www
    line = re.sub(r'„', ',', line)  # replace „ with ,
    # line = re.sub(r'<.*?>\s*\[/+\]|\S+?(\[>\])?\s*\[/+\]', '', line) # handling [/] [//] retracing

    # Batas Ampresand &
    line = re.sub(r'&=0', '', line)  # handling &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line)

    # Batas 0 dan [?] [!] [!!] and ↓
    line = re.sub(r'↓', '', line)  # handling ↓
    line = re.sub(r"0( \[[<>]\])? [.?!]$", '', line)
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # handling [?] [!] [!!]

    # FIXED!!!!
    line = re.sub(r'\+\<|\+\^|\^', '', line)  # delete +< and +^ and ^
    line = re.sub(r'<(.*)>\s*\[[<>]\]', r'\1', line)  # handling <...> [<] and <...>[>]
    line = re.sub(r'\[<\]|\[>\]', '', line)  # handling [<] and [>]
    # line = re.sub(r'[<>]', '', line) # handling < >

    line = re.sub(r'^[ .?!]*$', '', line)  # handling line with only space . ? !

    # line = re.sub(r'[\[\]\<\>\+]*', '', line) # left symbol

    # last clean

    line = utils.normalize_quotes(line)  # normalize quotation
    line = line.strip()
    line = utils.remove_multiple_spacing(line)
    return line + "\n"


import sys
import os
import re
import utils
from smart_open import open

d_in = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/MacWhinney/"
d_out = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/"

target_file_mw = "mc_whinney"
text_original_mw = ""
text_cleaned_mw = ""
n_files = 0
utils.profiling_init(utils)
print("\n===CHILDES data processing===\nOpening files in '" + d_in + "':")

for file in os.listdir(d_in):
    if file.endswith(".cha"):
        print(".", end="")
        n_files += 1
        with open(d_in + file, encoding='utf8', errors='ignore') as f:
            for line in f:
                prev_line = ""
                prev_cleaned_line = ""

                if line.startswith(("*MAR", "*CHI")):
                    text_original_mw += line
                    if prev_line != line and not utils.is_empty_line(line):
                        prev_line = line
                        cleaned_line_mw = clean(line)

                        # Check for duplicate and empty lines in cleaned text
                        if prev_cleaned_line != cleaned_line_mw and not utils.is_empty_line(cleaned_line_mw):
                            prev_cleaned_line = cleaned_line_mw
                            text_cleaned_mw += cleaned_line_mw

utils.report(n_files, text_original, text_cleaned)
utils.save(d_out, target_file, text_original, text_cleaned)
utils.profiling_end(utils)

print("\n" + "cleaning success!!")