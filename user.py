import pandas as pd
import numpy as np
from utils import *
from dataclasses import dataclass
import streamlit as st

'''
    1) This script contains the User class to instantiate user objects.
    2) This script is imported as a module.
'''

#######################
# Read Helper Data

bba_requirements = load_bba_requirements()
ge_mods = load_ge_requirements()

#######################
# UserProgression Class

@dataclass
class UserProgressSnapshot:
    filtered_data: pd.DataFrame
    total_units: int
    completion_rate: float
    cgpa: float
    current_year : int
    SU_used : int
    track_status : dict

#######################
# User Class

class User:
    
    # -- Initialize User object:

    def __init__(self, raw_data):

        self.raw_data = raw_data
        self.filtered_data = raw_data
        if 'Module_Type' in raw_data.columns:
            self.all_tracks = set(self.raw_data['Module_Type'].unique())
        else:
            self.all_tracks = None
            st.error("Can't seem to find [Module_Type] column in your data.")
        self.main_major = None
        self.snapshot = None # stores user computed metrics below
        self.init_cgpa =self.compute_cgpa(self.raw_data)
    
    # -- Store a new snapshot of updated metrics based on user's filter:

    def _generate_snapshot(self):
        filtered = self.filtered_data.copy()
        total_units = self.compute_total_MCs(filtered)
        cgpa = self.compute_cgpa(filtered)
        completion_rate = self.compute_completion_rate(filtered)
        current_year = self.compute_current_year(filtered)
        SU_used = self.compute_SUs(filtered)
        track_status = self.compute_progress(filtered)

        return UserProgressSnapshot(
            filtered_data=filtered,
            total_units=total_units,
            completion_rate=completion_rate,
            cgpa=cgpa,
            current_year = current_year,
            SU_used = SU_used,
            track_status=track_status
        )
    
    # -- Apply user's filter on raw data:

    def apply_filter(self, selected_tracks):
        if selected_tracks:
            unselected_tracks = set(self.all_tracks) - set(selected_tracks)
            unselected_mods = set(self.raw_data[self.raw_data['Module_Type'].isin(unselected_tracks)]['Module_Code'])
            self.filtered_data = self.raw_data[~(self.raw_data['Module_Code'].isin(unselected_mods))]
            self.snapshot = self._generate_snapshot()
        else:
            self.filtered_data = None
    
    # -- Return total MCs completed by user:

    def compute_total_MCs(self, data):

        # remove double-counted mods
        # remove any duplicated mods
        data = data.drop_duplicates(
            subset=['Module_Code', 'Module_Title', 'Year', 'Semester', 'Units', 'Grade', 'GPA', 'Term'], keep='first'
            )
    
        # for IP mods, count MCs for only 1 entry
        data = data.drop_duplicates(
            subset=['Module_Code', 'Module_Title', 'Units', 'Module_Type', 'Module_Type_UE'], keep='first'
            )
        
        if data.empty:
            return 0
        else:
            total = int(data['Units'].sum())
            return total
    
    def compute_completion_rate(self, data):
        total_MCs_requirement = 160
        total_MCs_completed = self.compute_total_MCs(data)
        return round((total_MCs_completed/ total_MCs_requirement)*100, 1)
    
    # -- Return user's CGPA:
    
    def compute_cgpa(self, data):
        data = data[~(data['Grade'].isin(["S", "IP", "NG"]))]

        # remove double-counted mods
        # remove any duplicated mods
        data = data.drop_duplicates(
            subset=['Module_Code', 'Module_Title', 'Year', 'Semester', 'Units', 'Grade', 'GPA', 'Term'], keep='first'
            )
        
        # for IP mods, just take the entry with max(Term) or Grade != IP

        if data.empty:
            return 0
        else:
            cgpa = np.sum(data['GPA'] * data['Units']) / sum(data['Units'])
            cgpa = round_half_up(cgpa)
            return cgpa
    
    # -- Return user's current year of study:

    def compute_current_year(self, data):
        return max(data['Year'].astype(int))
    
    # -- Return user's remaining SU count:

    def compute_SUs(self, data):
        if not data.empty:
            current_year = self.compute_current_year(data)
            if current_year <= 1:
                total_SUs = 32
                total_used = sum(data[data['Grade']=='S']['Units'])
            else:
                SUs_in_y1 = sum(data[(data['Year'] <= 1) & (data['Grade']=='S')]['Units'])
                remaining_SUs = 32 - SUs_in_y1
                bringover_SUs = 12
                total_used = sum(data[(data['Year'] >= 2) & (data['Grade']=='S')]['Units'])
                
                if remaining_SUs >= bringover_SUs:
                    total_SUs = 12
                else:
                    total_SUs = remaining_SUs

            return (total_SUs - total_used)
        else:
            return 32
    
    # -- Return user's academic progression { Module_Type : (Completion_Rate, Completion_Status, CGPA) }:

    def compute_progress(self, data): # data is filtered_data

        # Initialize academic progress for all tracks
        completion_status = {}
        all_tracks = list(self.all_tracks.union(set(data['Module_Type_UE'].unique())))
        for track in all_tracks: 
            completion_status[track] = None
        completion_status['BBA-FSP'] = None
        completion_status['BBA-BE'] = None
        completion_status['BBA-BF'] = None
        completion_status['GE'] = None
        completion_status['UE'] = None

        # Compute academic progress for all tracks

        for track in list(completion_status.keys()):
            if track == 'GE':
                completion_status[track] = self.compute_GE_progress(data)
            elif track == 'UE':
                completion_status[track] = self.compute_UE_progress(data)
            elif track =='BBA-BE':
                completion_status[track] = self.compute_BBA_CORE_progress(data, 'BBA-BE')
            elif track =='BBA-BF':
                completion_status[track] = self.compute_BBA_CORE_progress(data, 'BBA-BF')
            elif track =='BBA-FSP':
                completion_status[track] = self.compute_BBA_CORE_progress(data, 'BBA-FSP')
            elif track.startswith('BBA-'):
                completion_status[track] = self.compute_BBA_MAJ_progress(data, track)
            elif track.startswith("MAJOR-"):
                completed_MCs = sum(data[data['Module_Type']==track]['Units'])
                completion_rate = round(completed_MCs/ 40, 2)
                completion_status[track] = (
                    completion_rate,                                        # float
                    [f"{40 - completed_MCs} number of {track} electives"],  # list
                    self.compute_cgpa(data[data['Module_Type']==track])     # float
                )
            elif track.startswith("MINOR-"):
                completed_MCs = sum(data[data['Module_Type']==track]['Units'])
                completion_rate = round(completed_MCs / 20, 2)
                completion_status[track] = (
                    completion_rate,                                        # float
                    [f"{20 - completed_MCs} number of {track} electives"],  # list
                    self.compute_cgpa(data[data['Module_Type']==track])     # float
                )

        return completion_status
    
    # -- Return academic progression tuple (Completion_Rate, Completion_Status) for BBA-CORE (i.e BBA-BE, BBA-BE, BBA-FSP):

    def compute_BBA_CORE_progress(self, data, track:str):
    
        if not data.empty:

            required = set(bba_requirements.get(track, {}).get('Required_Courses', []))

            if track in data['Module_Type'].str.upper().unique():
                data = data[data['Module_Type']==track]
                completed = set(data['Module_Code'].str.upper())
                remaining = required - completed
                completion_rate = round(1 - (len(remaining)/len(required)), 2)
                completion_status = list(remaining)
                track_cgpa = self.compute_cgpa(data)
            else:
                completion_rate = 0
                completion_status = list(required)
                track_cgpa = 0

            return (completion_rate, completion_status, track_cgpa)

        else:
            return None
        
    # -- Return academic progression tuple (Completion_Rate, Completion_Status) for BBA-MAJOR:

    def compute_BBA_MAJ_progress(self, data, major):

        if not data.empty:
            
            if major == 'BBA-ACC':

                required = set(bba_requirements.get('BBA-ACC', {}).get('Required_Courses', []))

                if major in data['Module_Type'].str.upper().unique():
                    data = data[data['Module_Type']==major]
                    completed = set(data['Module_Code'].str.upper())
                    remaining = required - completed
                    completion_rate = round(1 - (len(remaining)/len(required)), 2)
                    completion_status = list(remaining)
                    track_cgpa = self.compute_cgpa(data)
                else:
                    completion_rate = 0
                    completion_status = list(required)
                    track_cgpa = 0
            
                return (completion_rate, completion_status, track_cgpa)

            elif major.startswith('BBA-') and major not in ['BBA-BE', 'BBA-BF', 'BBA-FSP']:

                L3000_done, L4000_done = False, False
                required = set(bba_requirements.get(major, {}).get('Required_Courses', []))
                # obtain level 3000 & level 4000 electives requirements:
                L3000_electives_info = bba_requirements.get(major, {})
                L3000_electives = set(L3000_electives_info.get("3000_Electives", {}).get("Courses", {}))
                L3000_required_units = L3000_electives_info.get("3000_Electives", {}).get("Required_Units", {})

                L4000_electives_info = bba_requirements.get(major, {})
                L4000_electives = set(L4000_electives_info.get("4000_Electives", {}).get("Courses", {}))
                L4000_required_units = L4000_electives_info.get("4000_Electives", {}).get("Required_Units", {})

                if major in data['Module_Type'].str.upper().unique():

                    data = data[data['Module_Type']==major]

                    # check required modules completion:
                    completed = set(data[data['Module_Type'] == major]['Module_Code'].str.upper())
                    remaining_required = required - completed

                    # obtain electives completed:
                    electives_completed = completed - (required & completed)

                    # check how many level 3000 & level 4000 electives completed:
                    num_L3000_completed = len(electives_completed & L3000_electives)
                    num_L4000_completed = len(electives_completed & L4000_electives)
                    
                    if num_L3000_completed == (L3000_required_units / 4): L3000_done = True
                    if num_L4000_completed == (L4000_required_units / 4): L4000_done = True

                    numerator = (len(completed) + num_L3000_completed + num_L4000_completed)
                    denominator = (len(required) + (L3000_required_units / 4) + (L4000_required_units / 4))

                    completion_rate = round(numerator / denominator, 2)
                    track_cgpa = self.compute_cgpa(data)

                    if L3000_done & L4000_done:
                        completion_status = list(remaining_required)
                    else:
                        completion_status = list(remaining_required) + \
                                    [f"{L3000_required_units-(num_L3000_completed * 4)} MCs of 3K {major} modules"] + \
                                    [f"{L4000_required_units-(num_L4000_completed * 4)} MCs of 4K {major} modules"]
                else:
                    completion_rate = 0
                    completion_status = list(required) + \
                                        [f"{L3000_required_units} MCs of 3K {major} modules"] + \
                                        [f"{L4000_required_units} MCs of 4K {major} modules"]
                    track_cgpa = 0

                return (completion_rate, completion_status, track_cgpa)
        else:
            return None

    # -- Return academic progression tuple (Completion_Rate, Completion_Status) for GE:
     
    def compute_GE_progress(self, data):

            if not data.empty:

                required_prefixes = {'GEA', 'GEI', 'GESS', 'GEN', 'GEC', 'GEX'}

                if 'GE' in data['Module_Type'].str.upper().unique():

                    data = data[data['Module_Type']=='GE']
                    completed = set(data['Module_Code'].str.upper())
                    required_prefixes_checker = required_prefixes.copy()

                    for completed_ge_mod in list(completed):
                        match = ge_mods[ge_mods['Module_Code'] == completed_ge_mod]
                        if not match.empty:
                            prefix = match.iloc[0]['Pillar']
                            required_prefixes_checker.remove(prefix)
                    completion_rate = round(1 - (len(required_prefixes_checker) / len(required_prefixes)), 2)
                    completion_status = list(required_prefixes_checker)
                    track_cgpa = self.compute_cgpa(data)

                else:
                    completion_rate = 0
                    completion_status = list(required_prefixes)
                    track_cgpa = 0
                return (completion_rate, completion_status, track_cgpa)
            
            else:
                return None
    
    # -- Return academic progression tuple (Completion_Rate, Completion_Status) for UE:

    def compute_UE_progress(self, data):

        if not data.empty:

            required_MCs = 48

            if 'UE' in data['Module_Type_UE'].str.upper().unique():
                
                data = data[data['Module_Type_UE']=='UE']

                completed_MCs = sum(data['Units'])
                completion_rate = round(completed_MCs / required_MCs, 2)
                completion_status = [f"{required_MCs - completed_MCs} number of UE MCs"]
                track_cgpa = self.compute_cgpa(data)
    
            else:
                completion_rate = 0
                completion_status = [f"{required_MCs} number of UE MCs"]
                track_cgpa = 0
            
            return (completion_rate, completion_status, track_cgpa)
        
        else:
            return None