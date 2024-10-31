import regex as re
import os
import time
import regex as rex
import psutil

global start_time, start_mem

def get_corpus_info(corpus):
    tokens = corpus.split()
    types = {}
    for t in tokens:
        if not t in types:
            types[t] = ""
    return len(types), len(tokens)


def space_punctuation(line):  
    line = re.sub(r'(\w)?([:;.!?…])(\w)?', r'\1\2\n\3', line) # split lines after strong punctuation
    line = re.sub(r'(\s)?([:;.!?…])(\s)*', r'\1\2\n', line) # split lines after strong punctuation
    line = re.sub('([.,:;!?()])', r' \1', line) # add space before punct
    line = re.sub(r'\. (\. )+', r' ... ', line)  # pauses
    line = re.sub('([,()])', r'\1 ', line) # add space after
    line = rex.sub(r'^[\p{P}\s]*', '', line.strip()) # remove initial useless punctuation
    line = rex.sub(r'\n[\p{P}\s]*', '\n', line) # remove initial useless punctuation
    return line


def space_symbols(line):
    line = re.sub(r'([*+#@§&%$£°])', r' \1 ', line)  # space symbols
    return line


def remove_symbols(line):
    line = re.sub(r'([*+\-#@§&%$£°_])', ' ', line)  # space symbols
    return line


def add_full_stop(line):  
    if not rex.search(r'\p{P}$', line):
        line += ' .'
    return line


def remove_multiple_spacing(line):
    line = re.sub(r'\s{2,}', ' ', line) # remove multiple spacing
    line = re.sub(r'\n{2,}', '\n', line) # remove multiple breaks
    return line


def remove_brackets(line):
    line = re.sub(r'[\[\]<>\(\){}]', '', line) # remove brackets
    line = re.sub(r'--*', '', line) # remove multiple dashes
    line = re.sub(r'^- *', '', line) # remove initial dash
    return line


def normalize_quotes(line):
    line = re.sub(r'[“‘’”""«»「」]', r' " ', line)
    return line


def remove_quotes(line):
    line = re.sub(r'[“‘’”""«»「」]', r' " ', line)
    return line


def is_empty_line(line):
    if len(line)>0 and line != "\n" and not rex.match(r'^[\s\p{P}]*$', line):
        return 0
    else:
        return 1


# reporting corpus information
def report(n_files, text_original, text_cleaned):
    print("\nNumber of files pre-processed: " + str(n_files))

    types, tokens = get_corpus_info(text_original)
    print("\nBefore cleaning:\nTypes: " + str(types) + "\nTokens: " + str(tokens) + "\nTTR: " + str(round(types/tokens,2)))
   
    types, tokens = get_corpus_info(text_cleaned)
    print("\nAfter cleaning:\nTypes: " + str(types) + "\nTokens: " + str(tokens) + "\nTTR: " + str(round(types/tokens,2)))


# Write original and cleaned text files
def save(d_out, target_file, text_original, text_cleaned):
    with open(d_out+"original/"+target_file, 'w', encoding='utf-8') as f:
        f.write(f"{text_original}")
   
    print("Original data stored in: " + d_out + "original/" + target_file)
   
    with open(d_out+target_file, 'w', encoding='utf-8') as f:
        f.write(f"{text_cleaned}")
    print("Pre-processed data stored in: " + d_out + target_file)


def measure_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return round(mem_info.rss / (1024 ** 2), 2)  # Convert bytes to MB


def profiling_init(self):
    self.start_time = time.time()
    self.start_mem = measure_memory()


def profiling_end(self):
    execution_time = round((time.time() - self.start_time) / 60, 0)
    memory_load = measure_memory() - self.start_mem
    print("Execution time: "+str(execution_time)+" min - Memory Load: "+str(memory_load)+" MB")