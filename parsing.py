# Import module required
import spacy
import benepar
from nltk import Tree
import pandas as pd

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)

# Upload the data to process
data = pd.read_csv("/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/childes_cleaned.csv")  # Please adjust your dir

# Parsing children speech
data['doc_objects'] = data['cleaned_speech'].apply(lambda text: nlp(text))


def sent_segmentation(doc):  # Function to filter out speech that are not sentences
    for sent in doc.sents:
        parse_tree = sent._.parse_string  # Get the constituency parsing
        tree = Tree.fromstring(parse_tree)

        if tree.label() in ['S', 'SBAR', 'SQ', 'SBARQ']:  # Check root label
            # Check if it has a verb
            verb = [token for token in sent if token.pos_ == 'VERB']
            if verb:
                return True
    return False


data = data[data['doc_objects'].apply(sent_segmentation)]

data.to_csv("/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/childes_parsed.csv")  # Please adjust your dir
