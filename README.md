# Child Syn Dev Automatic Measurement
This project aims to create an automated measurement of the development of children syntactic acquisition using machine learning technique based on the Growing Tree approach. The system will run two main processes: 1.) Structure identification and 2.) Machine learning classification

## Data Preprocessing
1. clean.py contains functions to clean noises in .CHA files
2. structure.py contains functions to filter sentence-speech and to identify certain structures
3. preprocess.py contains the code to process the corpus including cleaning the data and convert it from text to dataframe

## Parsing and Structure Identification
Using parsing_structureidf.py, the data is then parsed with Spacy and Benepar to get constituent trees. The output is use for structure identifier  


## Developmental Stage Classification

