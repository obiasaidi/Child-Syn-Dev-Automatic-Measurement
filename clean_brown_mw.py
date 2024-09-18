import regex as re
import utils
import sys
import os
from smart_open import open
import cleanch
import glob


# Cleaning Brown
dir_in ="/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/Brown/"
dir_out = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/Brown/"
target_file = "brown_clean.txt"
text_original = ""
text_cleaned = ""
n_files = 0
utils.profiling_init(utils)
print("\n===CHILDES data processing===\nOpening files in '" + dir_in + "':")

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
                        if prev_line != line and not utils.is_empty_line(line):
                            prev_line = line
                            cleaned_line = cleanch.preprocess(line)

                            # Check for duplicate and empty lines in cleaned text
                            if prev_cleaned_line != cleaned_line and not utils.is_empty_line(cleaned_line):
                                prev_cleaned_line = cleaned_line
                                text_cleaned += cleaned_line

utils.report(n_files, text_original, text_cleaned)
utils.save(dir_out, target_file, text_original, text_cleaned)
utils.profiling_end(utils)

print("\n"+"CLEANING BROWN SUCCESS!!")

# Cleaning MacWhinney

d_in = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/MacWhinney/"
d_out = "/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/"

target_file_mw = "mc_whinney_cleaned"
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
                        cleaned_line_mw = cleanch.clean(line)

                        # Check for duplicate and empty lines in cleaned text
                        if prev_cleaned_line != cleaned_line_mw and not utils.is_empty_line(cleaned_line_mw):
                            prev_cleaned_line = cleaned_line_mw
                            text_cleaned_mw += cleaned_line_mw

utils.report(n_files, text_original, text_cleaned)
utils.save(d_out, target_file, text_original, text_cleaned)
utils.profiling_end(utils)

print("\n" + "CLEANING MACWHINNEY SUCCESS")