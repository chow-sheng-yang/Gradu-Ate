import pandas as pd
import numpy as np
from NUSMods_API import *

df = pd.read_excel('module_info.xlsx', engine="openpyxl")

moduleCodes = df['Module_Code'].unique()
code_to_description = {code : get_module_description(code) for code in moduleCodes}
df['Module_Description'] = df['Module_Code'].map(code_to_description)

df.to_excel("module_info_with_descriptions.xlsx", index=False)