import regex as re
import utils

def fix_word(line):
    line = re.sub(r" em ", " them ", line)
    line = re.sub(r" ya |^ya ", " you ", line)
    line = re.sub(r" ta |^ta ", " to ", line)
    line = re.sub(r" hafta |^hafta ", " have to ", line)
    line = re.sub(r" sposta |^sposta ", " supposed to ", line)
    line = re.sub(r" hadta |^hadta ", " had to ", line)
    line = re.sub(r" hasta |^hasta ", " has to ", line)
    line = re.sub(r" needta |^needta ", " need to ", line)
    line = re.sub(r" useta |^useta ", " used to ", line)
    line = re.sub(r" outa |^outa ", " out of ", line)
    line = re.sub(r" oughta |^oughta ", " ought to ", line)
    line = re.sub(r"going a ", "going to ", line)
    return line+"\n"

def clean(line):
    line = ' '.join(line.strip().split())  # Remove extra spaces
    line = line[6:] # Remove the first 6 characters
    line = line.lower() # Convert text to lowercase
    line = re.sub(r' \d+_\d+-?', '', line.strip())  # Remove timestamp
    line = re.sub(r'\[- hun\].*[.!?]', '', line)  # Remove the whole string contain '[- hun]'
    line = re.sub(r'\[\+\s*\w+?\]', '', line)  # Remove patterns like [+ dia] [+ gram]
    
    # Handle patterns with [*]
    line = re.sub(r"\[\*\s*[mp]\]", '', line) # Remove patterns like [* m] or [* p]
    line = re.sub(r'[\wʃʌɪɯəɪˈʤʧ@]+\s*\[\*\s(\w{2,})\]', r'\1', line)  # Handle patterns like [* forgot] and [* that]
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*\]', r'\1', line) # Handle patterns like 'berg [: brig] [*]'
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*.+?\]', r'\1', line) # Handle patterns like 'I neededed [: needed] [* +ed-dup]'
    line = re.sub(r'\[\*\s[^m].+?\]', '', line) # Handle patterns like 'she [* s:r]'
    line = re.sub(r'\S+?\s*\[=\s*(.+?)\]\s*\[\*\]', r'\1', line) # Handle patterns like 'why [= because] [*]'
    line = re.sub(r'\S+?\s*\[\*\]\s*\[=\s*(.+?)\]', r'\1', line) # Handle patterns like 'Jophes [*] [= Joseph]'
    line = re.sub(r'\[\*\]', '[possible gram error]', line)  # Handle [*] in the patterns like 'the peoples [*]'
    
    # Handle patterns like [* m:    ]
    line = re.sub(r'\[\*\sm:=ed\]', '[past error]', line)  # Handle [*m:=ed]
    line = re.sub(r'\s*\[\*\sm:0(\w+).*?\]', r'\1', line)  # Handle [m:0 ] missing reg form
    line = re.sub(r'\[\*\sm:a\]', '[morph error]', line)  # Handle [*m:a] morph error
    line = re.sub(r"s \[\* m=s\]", '', line)  # Handle [* m=s] morph error
    
    # Handle [=!  ] [=?  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # Remove patterns like [=! wolf noises]
    line = re.sub(r'two months \[=\? (too much)\]', r'\1', line)  # Handle string 'two months [=? too much]'
    line = re.sub(r'\S+?\s*\[=\?\s*(.+?)\]', r'\1', line)  # Handle patterns like 'bobby [=? bottle]'
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # Remove patterns like [% ] or 0 [%  ]
    
    # Handle [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # Remove patterns like 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # Handle pattern like mhm [= yes]
    # This pattern doesnt have scope for the strings that are being corrected
    line = re.sub(r"\[=\s.+?\]", '', line)  # Handle patterns like 'don't say me that [= don't say that I hafta put on my socks]'

    # Handle patterns like dat [: that]
    line = re.sub(r"\S+ \[: (.+?)\]", r'\1', line)  # Handle dat [: that]

    line = re.sub(r'\[<\]|\[>\]', '', line) # Remove [<] and [>]
    line = re.sub(r'\+\.{2,3}', '[incomplete speech]', line)  # Handle +.. or +...
    line = re.sub(r'\+\+', '', line)  # Remove ++
    line = re.sub(r'\(\.+\)', '[PAUSE]', line)  # Replace (.) (..) (...) with [PAUSE]
    line = re.sub(r'\(|\)', '', line)  # Revise patterns like op(en) to be like open
    line = re.sub(r':', '', line)   # Remove : in patterns like mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # Remove _ in patterns like teddy_bear
    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # Replace xxx or yyy with [unintellegible speech]
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # Replace www with [untranscribed material]
    line = re.sub(r'„', ',', line)  # replace „ with ,

    # Handle Ampersand &
    line = re.sub(r'&=0', '', line)  # Remove patterns like &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line) # Remove patterns like &* &= &~ &+ &-

    # Handle 0 dan [?] [!] [!!] and ↓
    line = re.sub(r'↓', '', line)  # Remove ↓
    line = re.sub(r"0\s*[.?!]$", '', line) # Handle the lines only containing 0 and/or with space .?!
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # Remove [?] [!] [!!]
    
    line = re.sub(r'\+\<|\+\^|\^', '', line)  # Remove +< and +^ and ^
    
    # Handle repetition and retracing [/] [//]
    line = re.sub(r"<.+?>(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\S+?(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\s*\[/+\]", "", line)
    
    line = re.sub(r"[<>]", '', line) # Remove left <>

    line = re.sub(r'^[ .?!]*$', '', line)  # Remove space . ? ! in lines with only space . ? !
    line = fix_word(line) # Fix words like hafta sposta
    
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
