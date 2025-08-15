import pandas as pd
from utils import *
from functools import reduce
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import os

'''
    1) This script reads the demand and allocation report data and labels a Popularity Score for NUS BBA Electives based on:
        - Demand vs Vacancy Ratio;
        - Sustained Oversubscription %;
        - Demand Trend;
        - Demand Variation Score;
    2) This script is not a module;
    3) Run this script ONCE only.
'''

if __name__ == "__main__":

    #######################
    # Read Data

    file_path = './data'
    df = pd.read_csv(file_path+'/'+'demand_allocation.csv')

    bba_requirements = load_bba_requirements()
    bba_electives = return_all_bba_electives()
    bba_modtypes = return_flatten_bba_electives()

    #######################
    # Preprocessing

    # -- Fill NA & Replace "-" for Vacancy column:

    df.fillna(0, inplace=True)
    df['Vacancy'] = df['Vacancy'].replace('-', 0)

    # -- Convert Data Types:

    df['Faculty'] = df['Faculty'].astype(str)
    df['Department'] = df['Department'].astype(str)
    df['Module_Code'] = df['Module_Code'].astype(str)
    df['Module_Title'] = df['Module_Title'].astype(str)
    df['Class_Slot'] = df['Class_Slot'].astype(str)
    df['Vacancy'] = df['Vacancy'].astype(int)
    df['Demand'] = df['Demand'].astype(int)
    df['Round'] = df['Round'].astype(int)

    unique_terms = sorted(df['Academic_Term'].unique(), key=lambda x: (
        int(x[2:4]),  # AY start year
        int(x[-1])    # Semester
    ))

    df['Academic_Term'] = pd.Categorical(df['Academic_Term'], categories=unique_terms, ordered=True)
    df['Academic_Term'] = df['Academic_Term'].astype(str)

    # -- Fix Misspelled Strings:

    faculty_mapping = {
        'Faculty of Arts &\nSocial Sci' : 'College of Humanities & Sciences',
        'Faculty of\nEngineering' : 'Faculty of Engineering',
        'Faculty of Law' : 'Faculty of Law',
        'Faculty of Science' : 'College of Humanities & Sciences',
        'Multi Disciplinary\nProgramme' : 'Multi-Disciplinary Programme',
        'NUS' : 'NUS',
        'NUS Business\nSchool' : 'NUS Business School',
        'Residential College' : 'Residential College',
        'SSH School of\nPublic Health' : 'SSH School of Public Health',
        'School of\nComputing' : 'School of Computing',
        'School of Cont &\nLifelong Edun' : 'NUS SCALE',
        'School of Design &\nEnvironment' : 'College of Design & Engineering',
        'University Scholars\nProgramme' : 'University Scholars Programme',
        'YST Conservatory\nof Music' : 'YST Conversatory of Music', 
        'Yale-NUS College' : 'Yale-NUS College',
        'Yong Loo Lin Sch\nof Medicine' : 'YLL School of Medicine',
        'Yong Loo Lin Sch' : 'YLL School of Medicine',
        'YST Conservatory' : 'YST Conversatory of Music',
        'Coll. of Humanities\n& Sciences' : 'College of Humanities & Sciences',
        'SSH School of' : 'SSH School of Public Health',
        'University Scholars' : 'University Scholars Programme',
        'College of Design\nand Eng' : 'College of Design & Engineering',
        'Collg of Design &\nEngineering' : 'College of Design & Engineering',
        'Collg of Design &' : 'College of Design & Engineering',
        'NUS Graduate\nSchool' : 'NUS Graduate School',
        'Faculty of' : 'College of Design & Engineering',
        'College of Design' : 'College of Design & Engineering',
        'NUS College' : 'NUS College',
        'Faculty of Arts &' : 'College of Humanities & Sciences',
        'Risk Management\nInstitute' : 'Risk Management Institute',
        'NUS Business' : 'NUS Business School',
        'School of' : 'School of Computing',
        'School of Cont &' : 'NUS SCALE'
    }

    df['Faculty'] = df['Faculty'].map(faculty_mapping)

    #######################
    # Extracting Relevant BBA data (only)

    # -- Filter out only NUS Business data:

    df_business = df[df['Faculty'] == 'NUS Business School']

    # -- Filter out only Relevant Electives:

    df_business = df_business[df_business['Module_Code'].isin(bba_electives)]

    # -- Fill in Module_Type:

    df_business['Module_Type'] = df['Module_Code'].map(bba_modtypes)

    # -- Compressing Class Slots data:

    df_business = df_business.groupby(['Module_Code', 'Academic_Term', 'Round']).agg({
        "Faculty" : 'first',
        "Department" : 'first',
        "Module_Title" : 'first',
        "Vacancy" : 'sum',
        'Demand' : 'sum', 
        "Module_Type" : 'first'
    }).reset_index()

    #######################
    # Construct Metrics Dataframes

    # -- Demand-Vacancy Ratio:

    DVR = df_business.groupby('Module_Code')\
                    .agg({'Module_Title' : 'first',
                        'Module_Type' : 'first',
                        'Vacancy' : 'sum', 
                        'Demand' : 'sum'}) \
                    .reset_index() \
                    .rename(columns={'Vacancy' : 'Overall_Vacancy', 'Demand' : 'Overall_Demand'})

    DVR['DVR'] = DVR['Overall_Demand'] / DVR['Overall_Vacancy']

    # -- Sustained Oversubscription %:

    k = 3 # adjust where needed
    OPT = df_business.groupby(['Module_Code', 'Academic_Term']) \
                    .agg({'Vacancy':'sum', 'Demand':'sum'}) \
                    .reset_index() \
                    .rename(columns={'Vacancy':'Vacancy_per_term', 'Demand':'Demand_per_term'})
    OPT['Oversubscribed'] = (OPT['Demand_per_term'] > OPT['Vacancy_per_term']).astype(int)
    OPT = OPT.groupby("Module_Code")['Oversubscribed'] \
                    .agg(['mean','count']) \
                    .rename(columns={'mean':'Pct_Oversubscribed', 'count':'num_terms'}) \
                    .reset_index()
    OPT['Oversubscribed_weighted'] = (OPT['Pct_Oversubscribed'] * OPT['num_terms']) / (OPT['num_terms'] + k)

    # -- Simple Linear Regression Coefficient (Trend):

    def compute_LR(group):
        if len(group) < 2:
            return 0
        X = group['Term_Index'].values.reshape(-1, 1)
        y = group['Demand'].values
        model = LinearRegression().fit(X, y)
        return model.coef_[0]

    LR = df_business.groupby(['Module_Code', 'Academic_Term']).agg({'Demand':'sum', 'Vacancy':'sum'}).reset_index()
    LR['Academic_Term'] = pd.Categorical(LR['Academic_Term'], categories=unique_terms, ordered=True)
    LR['Term_Index'] = LR['Academic_Term'].cat.codes
    LR = LR.groupby("Module_Code").apply(compute_LR).reset_index(name='Demand_Trend')

    # -- Variation in Demand:

    VAR = df_business.groupby(['Module_Code', 'Academic_Term']).agg({'Demand':'sum'}).reset_index()
    VAR = VAR.groupby('Module_Code')['Demand'].agg(['mean', 'std']).reset_index()
    VAR['CoV'] = VAR['std'] / VAR['mean']
    VAR['CoV'].fillna(2.0, inplace=True)

    #######################
    # Final Ranking Output

    # -- Merge Dataframes:

    dfs = [DVR[['Module_Code', 'Module_Title', 'Module_Type', 'DVR']], 
        OPT[['Module_Code', 'Oversubscribed_weighted']], 
        LR[['Module_Code', 'Demand_Trend']], 
        VAR[['Module_Code', 'CoV']]]
    popularity_df = reduce(lambda left, right: pd.merge(left, right, on='Module_Code', how='inner'), dfs)

    # -- Scale Data:

    scaler = StandardScaler()

    popularity_df[['DVR_scaled', 'Oversubscribed_weighted_scaled', 'LR_Coefficient_scaled', 'CoV_scaled']] = scaler.fit_transform(
        popularity_df[['DVR', 'Oversubscribed_weighted', 'Demand_Trend', 'CoV']]
    )
    popularity_df['CoV_scaled'] = 1 - popularity_df['CoV_scaled']

    # -- Compute Overall Popularity Score:

    popularity_df['popularity_score'] = (
        0.3 * popularity_df['DVR_scaled'] +
        0.3 * popularity_df['Oversubscribed_weighted_scaled'] +
        0.25 * popularity_df['LR_Coefficient_scaled'] +
        0.15 * popularity_df['CoV_scaled']
    )

    final_ranking = popularity_df[['Module_Code', 
                                   'Module_Title', 
                                   'Module_Type', 
                                   'DVR_scaled',
                                   'Oversubscribed_weighted_scaled',
                                   'LR_Coefficient_scaled',
                                   'CoV_scaled',
                                   'popularity_score']].sort_values(by='popularity_score', ascending=False)

    bba_electives_demand_vacancy_data = df_business \
                                        .groupby(['Module_Code', 'Academic_Term']) \
                                        .agg({
                                            "Module_Title" : 'first',
                                            "Module_Type" : 'first',
                                            "Vacancy" : 'sum',
                                            'Demand' : 'sum', 
                                        }).reset_index()
    
    # -- Output:
    
    print(f"Saved 2 files bba_electives_ranking.pkl and bba_electives_flatten_ranking.pkl in path location: {os.getcwd()}")
    with open('bba_electives_ranking.pkl', 'wb') as f:
        pickle.dump(final_ranking, f)

    with open('bba_electives_demand_vacancy_data.pkl', 'wb') as f:
        pickle.dump(bba_electives_demand_vacancy_data, f)