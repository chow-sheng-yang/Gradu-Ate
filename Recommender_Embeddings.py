import pandas as pd
from utils import *
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import os
nltk.download("punkt")

'''
    1) This script generates embeddings for Career Tags and Modules' Descriptions for the Recommendation System
    2) This script is not a module;
    3) Run this script ONCE only.
'''

#######################
# Function to clean and combine LinkedIn descriptions and OpenAI descriptions:

def preprocess_and_combine(role_desc_short: str, linkedin_desc: str):
    """
    Clean and preprocess role descriptions.
    Combines a short description with LinkedIn description,
    while extracting {company: role} mapping.
    """
    
    def preprocess_text(text):
        """Lowercase, remove numbers, non-alphanumeric chars, and stopwords."""
        if not isinstance(text, str):
            return ""
        
        text = text.lower()
        processed_chars = []
        i = 0
        while i < len(text):
            if text[i].isdigit():  # remove numbers/tokens containing digits
                while i < len(text) and text[i] != ' ':
                    i += 1
            elif text[i].isalnum() or text[i].isspace():  
                processed_chars.append(text[i])
            i += 1
        
        processed_text = ''.join(processed_chars)
        tokens = word_tokenize(processed_text)
        stop_words = set(stopwords.words("english"))
        tokens = [word for word in tokens if word not in stop_words]
        
        return " ".join(tokens)

    # --- Step 2: Remove the leading (Company) part from LinkedIn text
    linkedin_desc = re.sub(r"^\([^)]*\)\s*", "", linkedin_desc)
    
    # --- Step 3: Replace line breaks & multiple spaces
    linkedin_desc = re.sub(r"\s+", " ", linkedin_desc).strip()
    
    # --- Step 4: Preprocess both texts (using your module preprocessing logic)
    linkedin_clean = preprocess_text(linkedin_desc)
    short_clean = preprocess_text(role_desc_short)
    
    # --- Step 5: Combine
    combined = f"{short_clean} {linkedin_clean}".strip()
    
    return combined


#######################
# Read data

module_descriptions = load_bba_electives_description()
careers_df = load_careers()

#######################
# Preprocessing

# -- Filter out Independent Study modules:

exclude = [
    'DBA3751',
    'DBA3752',
    'DBA4751',
    'DBA4752',
    'BSN3751',
    'BSN4751',
    'BSE3751',
    'BSE4751',
    'MNO3751',
    'MNO3752',
    'MNO4751',
    'MNO4752',
    'FIN3751',
    'FIN3752',
    'FIN4751',
    'FIN4752',
    'MKT3751',
    'MKT3752',
    'MKT4751',
    'MKT4752',
    'DOS3751',
    'DOS3752',
    'DOS4751',
    'DOS4752',
    'ACC4751'
            ]

# -- Prepare modules data for vector embedding:

modules_df = module_descriptions.copy()
modules_df = modules_df.drop_duplicates(subset=['Module_Code']).reset_index(drop=True)
modules_df['Module_Title+Description'] = modules_df['Module_Title'] + " " + modules_df['Module_Description']
modules_df = modules_df[~(modules_df['Module_Code'].isin(exclude))].reset_index(drop=True)

# -- Prepare career tag data for vector embedding:

careers_df.columns = ["Major", 
                    "Career", 
                    "OpenAI_Description", 
                    "LinkedIn_Description_1",
                    "LinkedIn_Description_2",
                    "LinkedIn_Description_3"]
careers_df.drop_duplicates(subset=['Career']).reset_index(drop=True)

careers_df['LI_Description_All'] = careers_df[["LinkedIn_Description_1", "LinkedIn_Description_2", "LinkedIn_Description_3"]] \
                                    .apply(lambda row : " ".join([x for x in row if pd.notnull(x)]), axis=1)
careers_df['cleaned_descriptions'] = careers_df[['OpenAI_Description', 'LI_Description_All']] \
                                    .apply(lambda row : preprocess_and_combine(row['OpenAI_Description'], row['LI_Description_All']), axis=1)

#######################
# Run Main Script

if __name__ == "__main__":

    # -- Initialize pre-trained Sentence Embedding model:

    model = SentenceTransformer('paraphrase-mpnet-base-v2')

    # -- Vectorize Career Tags (K):

    CE = model.encode(careers_df['cleaned_descriptions'], convert_to_tensor=True)
    print("Dimensions of Career-Tag Embeddings:\n", CE.shape, "\n")

    # -- Vectorize Module Descriptions (M):

    ME = model.encode(modules_df['Module_Description'], convert_to_tensor=True)
    print("Dimensions of Module Description Embeddings:\n", ME.shape, "\n")

    # -- Output:

    CE_df = pd.DataFrame(CE.cpu().numpy(), index=careers_df['Career'])
    CE_df.to_csv("Career-Tag_embeddings.csv")

    ME_df = pd.DataFrame(ME.cpu().numpy(), index=modules_df['Module_Code'])
    ME_df.to_csv("Module-Description_embeddings.csv")

    print(f"Saved 2 files Career-Tag_embeddings.csv and Module-Description_embeddings.csv in path location: {os.getcwd()}")