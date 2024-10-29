# Child Syn Dev Automatic Measurement
This project aims to create an automated measurement of the development of children syntactic acquisition using The Growing Tree approach

## Data Preprocessing
1. clean.py contains functions to clean noises in childes files
2. utils.py contains a list of another functions to clean noises in childes files
3. preprocess.py contains the code to process (including the cleaning) the corpora from text to a dataframe

## Parsing
1. Using parsing.py, the doc objects is created containing linguistic information for further analysis
2. Also, sentence segmentation is done by filtering out those speech that do not follow specific patterns based on constituency trees

