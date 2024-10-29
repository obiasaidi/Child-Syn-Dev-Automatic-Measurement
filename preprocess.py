import os
import pandas as pd
import clean


# Function to extract the corpus, age, and CHI speeches from .cha files and make a df
def text_to_df(d_in):
    corpus = []
    ages = []
    original_speeches = []

    for file in os.listdir(d_in):
        print(".", end="")
        with open(d_in + file, encoding='utf8') as f:
            corpus_name = ''
            child_age = ''

            for line in f:
                # Extract corpus and ages from the @ID line
                if line.startswith("@ID:") and "|CHI|" in line:
                    parts = line.split('|')
                    corpus_name = parts[1].strip()  # Corpus (e.g., "Brown")
                    child_age = parts[3].strip()  # Age (e.g., "2;03.04")

                # Extract speeches starting with *CHI:
                if line.startswith("*CHI:"):
                    # ori_speech = line.split(":", 1)[1].strip()  # Take only the speech
                    ori_speech = line.strip()  # Take also the *CHI

                    # Append all variable
                    corpus.append(corpus_name)
                    ages.append(child_age)
                    original_speeches.append(ori_speech)

        # Create a dataframe
        df = pd.DataFrame({
            'corpus': corpus,  # Same corpus value for all rows
            # 'child_name': ['adam'] * len(original_speeches),  # Change the name accordingly
            'child_age': ages,  # Same age for all rows
            'ori_speech': original_speeches  # The list of speeches
        })

    return df


data = text_to_df("/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/Brown/Adam/")  # Please Adjust your dir


#  Convert age to month (Use when there found child_age column is empty)
def convert_age_month(age_str):
    try:
        # Split the string into year and month.day
        year_month = age_str.split(';')
        if len(year_month) < 2 or not year_month[0].isdigit():  # Check if format is correct
            return None

        year = int(year_month[0])  # Convert year part to integer

        # Handle month.day part safely
        month_day = year_month[1].split('.')
        month = int(month_day[0]) if month_day[0].isdigit() else 0  # Convert month part

        # Calculate the age in months
        total_months = year * 12 + month
        return total_months

    except (ValueError, IndexError):  # Handle any potential errors
        return None


data['age_month'] = data['child_age'].apply(convert_age_month)
data = data[['corpus', 'child_age', 'age_month', 'ori_speech']]

# Preprocess children speech
data['cleaned_speech'] = data['ori_speech'].apply(clean.preprocess)


# Drop duplicate lines
data = data.drop_duplicates(subset=['cleaned_speech'])

# Dropping unnecessary speech for line
patterns = [
    r'^\s*[.?!]*\s$',                      # Pattern 1
    r'^\s*[\w@\'-]*(\s*[.!?])?$',          # Pattern 2
    r'^\s*[\w@\'-]*\s*<UNK>\s*[.!?]*$',    # Pattern 3
    r'^\s*xxx\s*[.!?]*$',                  # Pattern 4
    r'^\s*yyy\s*[.!?]*$',                  # Pattern 4
    r'^\s*www\s*[.!?]*$',                  # Pattern 4
    r'^\s*$'                               # empty string
]

patterns_to_drop = '|'.join(patterns)

data_cleaned = data[~data['cleaned_speech'].str.match(patterns_to_drop, na=False)]

# Save the dataframe to csv file
data_cleaned.to_csv("/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/childes_cleaned.csv")  # Please Adjust your dir

print("process done!!")
