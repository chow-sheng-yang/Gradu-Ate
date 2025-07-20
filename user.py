import pandas as pd
import numpy as np
from helper_functions import *
from dataclasses import dataclass

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
    grade_distribution: dict
    track_completion_df: pd.DataFrame
    track_remaining: dict


#######################
# User Class

class User:

    def __init__(self, raw_data):

        self.raw_data = raw_data
        self.filtered_data = raw_data
        self.all_tracks = self.raw_data['Module_Type'].unique()
        self.main_track = None
        self.double_counted_mods = None
        self.snapshot = None # stores user computed metrics below
    
    def _generate_snapshot(self):
        filtered = self.filtered_data.copy()
        total_units = self.compute_total_MCs(filtered)
        cgpa = self.compute_cgpa(filtered)
        completion_rate = self.compute_completion_rate(filtered)
        current_year = self.compute_current_year(filtered)
        SU_used = self.compute_SU_used(filtered)

        grades = list(get_grade_mapping().keys())
        full_grade_dist = {grade : 0 for grade in grades}
        grade_dist = filtered['Grade'].value_counts().to_dict()
        full_grade_dist.update(grade_dist)
        
        track_completion_df, track_remaining = self.compute_individual_track_progress(filtered)

        return UserProgressSnapshot(
            filtered_data=filtered,
            total_units=total_units,
            completion_rate=completion_rate,
            cgpa=cgpa,
            current_year = current_year,
            SU_used = SU_used,
            grade_distribution=full_grade_dist,
            track_completion_df=track_completion_df,
            track_remaining=track_remaining
        )

    def apply_filter(self, selected_tracks):
        if selected_tracks:
            unselected_tracks = set(self.all_tracks) - set(selected_tracks)
            unselected_mods = set(self.raw_data[self.raw_data['Module_Type'].isin(unselected_tracks)]['Module_Code'])
            self.filtered_data = self.raw_data[~(self.raw_data['Module_Code'].isin(unselected_mods))]

        else:
            self.filtered_data = None
        self.snapshot = self._generate_snapshot()

    def set_main_track(self, main_track):
        self.main_track = main_track
    
    def set_double_counts(self, dc_modules):
        self.double_counted_mods = list(dc_modules)

    def get_filtered_data(self):
        return self.filtered_data
    
    def compute_total_MCs(self, data):
        data = data.drop_duplicates(subset='Module_Code', keep='first')
        return int(data['Units'].sum()) 
    
    def compute_completion_rate(self, data):
        total_MCs_requirement = 160
        total_MCs_completed = self.compute_total_MCs(data)
        return round((total_MCs_completed/ total_MCs_requirement)*100, 1)
    
    def compute_cgpa(self, data):
        data = data[~(data['Grade'] == "S")]
        data = data.drop_duplicates(subset='Module_Code', keep='first')
        cgpa = round(np.sum(data['GPA'] * data['Units']) / sum(data['Units']), 2)
        return cgpa
    
    def compute_current_year(self, data):
        return max(data['Year'].astype(int))
    
    def compute_SU_used(self, data):
        return int(data[data['Grade'] == 'S'].shape[0])

    def compute_individual_track_progress(self, data):

        completion_status = {}
        remaining_status = {}

        for track in data['Module_Type'].unique():

            if track == 'BBA-HONS': # need to fix this:
                completed_MCs = data[data['Module_Type'] == track]['Units'].sum()
                required_MCs = get_track_requirements(track=track, type="MCs_required")
                completion_status[track] = round((completed_MCs / required_MCs)*100, 2)
                remaining_status[track] = []

            elif track == 'BBA-CORE':
                completed_modules = set(data[data['Module_Type'] == 'BBA-CORE']['Module_Code'])
                required_modules = set(get_track_requirements(track=track, type="Required_Courses"))
                remaining_modules = list(required_modules - completed_modules)
                completion_status[track] = round((len(completed_modules & required_modules) / len(required_modules))*100, 2)
                remaining_status[track] = remaining_modules

            elif track == 'GE':
                completed_modules = set(data[data['Module_Type'] == 'GE']['Module_Code'])
                required_modules =  set(get_track_requirements(track=track, type="Required_Courses"))
                remaining_modules = [prefix for prefix in required_modules if not any(item.startswith(prefix) for item in completed_modules)]
                completion_status[track] = round((len(required_modules - set(remaining_modules)) / len(required_modules))*100, 2)
                remaining_status[track] = remaining_modules

            elif track == 'UE':
                data_copy = data.copy()
                data_copy['New_Module_Type'] = data_copy['Module_Type'].apply(
                        lambda x : (
                            x if x in ['BBA-CORE', 'GE', 'BBA-HONS', 'UE', self.main_track] else
                            'UE' if x.startswith('MINOR-') else
                            'UE' if x.startswith('MAJOR-') else
                            'UE'
                        )
                    )
                num_completed_modules = data_copy[data_copy['New_Module_Type'] == 'UE'].shape[0] # number of rows = number of UEs
                num_required_modules = get_track_requirements(track=track, type='Num_Remaining_Electives')
                num_remaining_modules = num_required_modules - num_completed_modules
                completion_status[track] = round((num_completed_modules / num_required_modules)*100, 2)
                if num_remaining_modules > 0:
                    remaining_status[track] = [f"{int(num_remaining_modules)} number of {track} electives"]
            
            elif track.startswith('BBA-') and track != 'BBA-CORE':
                    completed_modules = set(data[data['Module_Type'] == track]['Module_Code'])
                    required_modules = set(get_track_requirements(track=track, type="Required_Courses"))
                    remaining_compulsory_modules = required_modules - completed_modules
                    num_remaining_non_compulsory_modules = get_track_requirements(track=track, type="Num_Remaining_Electives") - \
                                            len(completed_modules - (required_modules & completed_modules))
                    completion_status[track] = round((len(completed_modules) / (len(required_modules) + get_track_requirements(track=track, type="Num_Remaining_Electives")))*100, 2)
                    if num_remaining_non_compulsory_modules > 0:
                        remaining_status[track] = list(remaining_compulsory_modules) + [f"{int(num_remaining_non_compulsory_modules)} number of {track} electives"]
                    else:
                        remaining_status[track] = list(remaining_compulsory_modules)
 
            elif track.startswith('MINOR-') or track.startswith('MAJOR-'): # need to fix this:
                    completed_MCs = data[data['Module_Type'] == track]['Units'].sum()
                    required_MCs = get_track_requirements(track=track)
                    completion_status[track] = round((completed_MCs / required_MCs)*100, 2)
                    remaining_status[track] = []
        
        completion_status = pd.DataFrame(completion_status.items(), columns=['Module_Type', 'Completion_Rate'])

        return completion_status, remaining_status.items()