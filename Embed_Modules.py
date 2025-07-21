import pandas as pd
import numpy as np
from NUSMods_API import *
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
import pickle

def preprocess_text(text):                  # -- https://github.com/anuragjain-git/text-classification/blob/main/model.py
   
    if not isinstance(text, str):
        return ""
   
    text = text.lower() # Convert to lowercase
    processed_chars = [] # Initialize empty list to store processed characters
    i = 0
    while i < len(text):
        if text[i].isdigit(): # If character is a digit, skip all characters until the next space
            while i < len(text) and text[i] != ' ':
                i += 1
        elif text[i].isalnum() and not text[i].isdigit() or text[i].isspace(): # If character is alphanumeric or space, add it to processed_chars
            processed_chars.append(text[i])
        i += 1
    
    processed_text = ''.join(processed_chars) # Join the processed characters into a string
    tokens = word_tokenize(processed_text) # Tokenization
    stop_words = set(stopwords.words('english')) # Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)


if __name__ == "__main__":

    #######################
    # Read Data

    df = pd.read_excel('module_info.xlsx', engine="openpyxl")

    moduleCodes = df['Module_Code'].unique()
    code_to_description = {code : get_module_description(code) for code in moduleCodes}
    df['Module_Description'] = df['Module_Code'].map(code_to_description)

    #######################
    # Text Preprocessing

    df['Module_Description'] = df['Module_Description'].apply(preprocess_text)
    df['Module_Description'] = df['Module_Description'].fillna("")

    #######################
    # Save 

    print(df)
    
    with open('course_descriptions.pkl', 'wb') as f:
        pickle.dump(df, f)

