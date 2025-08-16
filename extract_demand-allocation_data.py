from pathlib import Path
import pdfplumber
import pandas as pd
import os

'''
    1) This script scrapes CourseReg Demand Allocation Report data from AY20-21 Semester 2 to AY25/26 Semester 1;
    2) Run this script ONCE only.
'''

if __name__ == "__main__":

    #######################
    # Set base directory to where NUS-ModReg-Reports is located

    base_dir = Path("../NUS-ModReg-Reports") # https://github.com/Bryce-3D/NUS-ModReg-Reports/tree/main

    #######################
    # Set the folder to start from {skip_until} (inclusive)

    skip_until = "AY20-21-Sem-2"
    start_collecting = False

    #######################
    # Save output in a list

    all_data = []

    #######################
    # Extract data

    # -- For each folder in sorted order:

    for folder in sorted(base_dir.iterdir()):
        if not folder.is_dir():
            continue
        folder_name = folder.name

        # -- Skip folder until target folder is reached:
        
        if not start_collecting:
            if skip_until in folder_name:
                start_collecting = True
            else:
                continue
        
        # -- Find matching DemandAllocation PDF files:

        for pdf_file in folder.glob("DemandAllocationRptUG_*.pdf"):
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            df = pd.DataFrame(table[2:], columns=table[0])
                            if "Demand" in df.columns:
                                df = df.loc[:, :'Demand']  # Keep only columns up to "Demand"

                            # -- Preprocessing:

                            df.columns = ['Faculty', 'Department', 'Module_Code', 'Module_Title', 'Class_Slot', 'Vacancy', 'Demand']
                            df = df.dropna(subset=['Module_Code', 'Module_Title', 'Class_Slot', 'Vacancy', 'Demand'], how='all')
                            df["Academic_Term"] = folder_name
                            df['Round'] = int(pdf_file.stem.split('_')[-1][1:])
                            all_data.append(df)
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")

    # -- Combine all PDF data & save:

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('demand_allocation.csv', index=False)
        print(f"Saved 1 file demand_allocation.csv in path location: {os.getcwd()}")
    else:
        print("No data extracted.")