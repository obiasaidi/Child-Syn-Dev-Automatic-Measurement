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
    return line

def gram(line):
    line = re.sub(r'\$n', '-[NOUN]', line)
    line = re.sub(r'\$v', '-[VERB]', line)
    line = re.sub(r'\$adj', '-[ADJ]', line)
    line = re.sub(r'\$inf', '-[INF]', line)
    return line


def preprocess(line):
    line = ' '.join(line.strip().split())  # Remove extra spaces
    line = line[6:]  # Remove the first 6 characters
    line = line.lower()  # Convert text to lowercase

    # Handle patterns with [+  ] or [*  ]
    line = re.sub(r'\[\+ \w+?\]', '', line)  # Remove patterns like [+ imit] [+ res] [+ imp]
    line = re.sub(r"\S+ \s*\[:\s*(.+?)\]\s*(\[\*.*?\])?", r'\1 ',
                  line)  # Handle patterns like [: of] [* fill] and [: beat] [* +ed]
    line = re.sub(r"\[\*( .*)?\]", '', line)  # Remove patterns like [*] and [* +s]

    # Handle patterns with [=?  ] [=!  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # Remove patterns like [=! wolf noises]
    line = re.sub(r'\S+?\s*\[=\?\s(.+?)\]', r'\1', line)  # Replace patterns like [=? too much]
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # Remove patterns like [% ] or 0 [%  ]

    # Handle [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # Remove patterns like 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # Handle patterns like [= yes]
    line = re.sub(r"\[=\s.+?\]", '',
                  line)  # Handle patterns like don't say me that [= don't say that I hafta put on my socks]

    # Handle Ampersand &
    line = re.sub(r'&=0', '', line)  # Remove patterns like &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line)  # Remove patterns like &* &= &~ &+ &-

    line = re.sub(r'„', ',', line)  # Replace „ with ,
    line = re.sub(r'\+\<|\+\^|\^', '', line)  # Remove +< and +^ and ^
    line = re.sub(r'\+\.\.\.', '[incomplete speech]', line)  # Replace +... with [incomplete speech]
    line = re.sub('↫.*?↫', '', line)  # Remove text between '↫' symbols
    line = re.sub(r'\(\.+\)', '[PAUSE]', line)  # Replace (.) (..) (...) with [PAUSE]
    line = re.sub(r'\(|\)', '', line)  # Revise patterns like op(en) to be like open
    line = re.sub(r':', '', line)  # Remove : in patterns like mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # Remove _ in patterns like teddy_bear
    line = utils.normalize_quotes(line)  # normalize quotation
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # Remove [?] [!] [!!]
    line = re.sub(r'0', '', line)  # Remove 0
    line = re.sub(r'\[<\]|\[>\]', '', line)  # Remove [<] and [>]

    # Handle repetition and retracing [/] [//]
    line = re.sub(r"<.+?>(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\S+?(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\s*\[/+\]", "", line)
    line = re.sub(r'[<>]', '', line)  # Remove unnecessary/left < >

    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # Replace xxx or yyy with [unintellegible speech]
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # Replace www with [untranscribed material]

    line = re.sub(r'^[ .?!]*$', '', line)  # Remove space .?! in the lines with only space . ? !
    line = fix_word(line)  # Fix words like hafta sposta
    line = gram(line)  # Fix gram pattern $
    line = line.strip(' ')  # Remove leading and trailing space
    line = utils.remove_multiple_spacing(line)  # Handle multiple spaces
    return line + "\n"


def clean(line):
    line = ' '.join(line.strip().split())  # Remove extra spaces
    line = line[6:]  # Remove the first 6 characters
    line = line.lower()  # Convert text to lowercase
    line = re.sub(r' \d+_\d+-?', '', line.strip())  # Remove timestamp
    line = re.sub(r'\[- hun\].*[.!?]', '', line)  # Remove the whole string contain '[- hun]'
    line = re.sub(r'\[\+\s*\w+?\]', '', line)  # Remove patterns like [+ dia] [+ gram]

    # Handle patterns with [*]
    line = re.sub(r"\[\*\s*[mp]\]", '', line)  # Remove patterns like [* m] or [* p]
    line = re.sub(r'[\wʃʌɪɯəɪˈʤʧ@]+\s*\[\*\s(\w{2,})\]', r'\1', line)  # Handle patterns like [* forgot] and [* that]
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*\]', r'\1', line)  # Handle patterns like 'berg [: brig] [*]'
    line = re.sub(r'\S+?\s*\[:\s*(.+?)\]\s*\[\*.+?\]', r'\1', line)  # Handle patterns like 'I neededed [: needed] [* +ed-dup]'
    line = re.sub(r'\[\*\s[^m].+?\]', '', line)  # Handle patterns like 'she [* s:r]'
    line = re.sub(r'\S+?\s*\[=\s*(.+?)\]\s*\[\*\]', r'\1', line)  # Handle patterns like 'why [= because] [*]'
    line = re.sub(r'\S+?\s*\[\*\]\s*\[=\s*(.+?)\]', r'\1', line)  # Handle patterns like 'Jophes [*] [= Joseph]'
    line = re.sub(r'\[\*\]', '[possible gram error]', line)  # Handle [*] in the patterns like 'the peoples [*]'

    # Handle patterns like [* m:    ]
    line = re.sub(r'\[\*\sm:=ed\]', '[past error]', line)  # Handle [*m:=ed]
    line = re.sub(r'\s*\[\*\sm:0(\w+).*?\]', r'\1', line)  # Handle [m:0 ] missing reg form
    line = re.sub(r'\[\*\sm:a\]', '[morph error]', line)  # Handle [*m:a] morph error
    line = re.sub(r"s|s*\[\* m=s\]", '', line)  # Handle [* m=s] morph error

    # Handle [=!  ] [=?  ] [%  ]
    line = re.sub(r'0?\s*\[=!\s.+?\](\s*\.)?', '', line)  # Remove patterns like [=! wolf noises]
    line = re.sub(r'two months \[=\? (too much)\]', r'\1', line)  # Handle string 'two months [=? too much]'
    line = re.sub(r'\S+?\s*\[=\?\s*(.+?)\]', r'\1', line)  # Handle patterns like 'bobby [=? bottle]'
    line = re.sub(r"(0\s*)?\[%.+?\](\s*\.)?", '', line)  # Remove patterns like [% ] or 0 [%  ]

    # Handle [=  ]
    line = re.sub(r'0\s*\[=\s.+?\](\s*\.)?', '', line)  # Remove patterns like 0 [=   ]
    line = re.sub(r"\S+\s*\[=\s([\w'@]+?)\]", r'\1', line)  # Handle pattern like mhm [= yes]
    # This pattern doesnt have scope for the strings that are being corrected
    line = re.sub(r"\[=\s.+?\]", '',line)  # Handle patterns like 'don't say me that [= don't say that I hafta put on my socks]'

    # Handle patterns like dat [: that]
    line = re.sub(r"\S+ \[: (.+?)\]", r'\1', line)  # Handle dat [: that]

    line = re.sub(r'\[<\]|\[>\]', '', line)  # Remove [<] and [>]
    line = re.sub(r'\+\.{2,3}', '[incomplete speech]', line)  # Handle +.. or +...
    line = re.sub(r'\+\+', '', line)  # Remove ++
    line = re.sub(r'\(\.+\)', '[PAUSE]', line)  # Replace (.) (..) (...) with [PAUSE]
    line = re.sub(r'\(|\)', '', line)  # Revise patterns like op(en) to be like open
    line = re.sub(r':', '', line)  # Remove : in patterns like mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # Remove _ in patterns like teddy_bear
    line = re.sub(r'„', ',', line)  # replace „ with ,

    # Handle Ampersand &
    line = re.sub(r'&=0', '', line)  # Remove patterns like &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line)  # Remove patterns like &* &= &~ &+ &-

    # Handle 0 dan [?] [!] [!!] and ↓
    line = re.sub(r'↓', '', line)  # Remove ↓
    line = re.sub(r"0\s*[.?!]$", '', line)  # Handle the lines only containing 0 and/or with space .?!
    line = re.sub(r'\[[\?]\]|\[!+\]', '', line)  # Remove [?] [!] [!!]

    line = re.sub(r'\+\<|\+\^|\^', '', line)  # Remove +< and +^ and ^

    # Handle repetition and retracing [/] [//]
    line = re.sub(r"<.+?>(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\S+?(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\s*\[/+\]", "", line)

    line = re.sub(r'(x|y){2,3}', '[unintellegible speech]', line)  # Replace xxx or yyy with [unintellegible speech]
    line = re.sub(r'w{2,3}', '[untranscribed material]', line)  # Replace www with [untranscribed material]

    line = re.sub(r"[<>]", '', line)  # Remove left <>

    line = re.sub(r'^[ .?!]*$', '', line)  # Remove space . ? ! in lines with only space . ? !
    line = fix_word(line)  # Fix words like hafta sposta

    line = utils.normalize_quotes(line)  # normalize quotation
    line = gram(line)  # Fix gram pattern $
    line = line.strip()
    line = utils.remove_multiple_spacing(line)
    return line + "\n"
