import spacy
import benepar
import pandas as pd
import structure

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)

data = pd.read_csv("/Users/robiatualaddawiyah/Documents/College/Year_2/LPT/NLP_project/Data/to_parse_5k.csv")

# Parsing children speech
print("Start parsing ...")

data['doc_objects'] = data['cleaned_speech'].apply(lambda text: nlp(text))

print("Parsing DONE!")

sentence_parsed = data[data['doc_objects'].apply(structure.sent_segmentation)]

sentence_parsed['parse_trees'] = sentence_parsed['doc_objects'].apply(lambda doc: ' '.join([sent._.parse_string for sent in doc.sents]))
sentence_parsed['structure'] = sentence_parsed['doc_objects'].apply(structure.struct_idf)

parsed = sentence_parsed[['corpus', 'age_month', 'ori_speech', 'cleaned_speech', 'structure', 'parse_trees']]

print(parsed.head())

parsed.to_csv("/Users/robiatualaddawiyah/Documents/College/Year_2/LPT/NLP_project/Data/data_with_structure.csv")

print("DONE!!!")


