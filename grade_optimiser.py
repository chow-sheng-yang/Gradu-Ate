from gurobipy import Model, GRB, quicksum
from helper_functions import get_grade_mapping

class GradeOptimizer:

    def __init__(self, df, threshold, lambda_penalty=0.05):

        self.df = df.copy()
        self.df = self.df[~(self.df['Grade'] == "S")]
        self.df = self.df.drop_duplicates(subset='Module_Code', keep='first')

        self.optimal_grade = threshold
        self.lambda_penalty = lambda_penalty

        self.sim_modules = ['SIM1000', 'SIM2000', 'SIM3000', 'SIM4000', 'SIM5000']
        self.sim_units = {mod: 4 for mod in self.sim_modules}

        self._grade_mapping = get_grade_mapping()
        self._letter_grades = list(self._grade_mapping.keys())
        self._gpa_grades = list(self._grade_mapping.values())
        self._num_grades = len(self._letter_grades)
        self.penalties = [3, 3, 2.5, 2, 1.5, 1, 0.8, 0.6, 0.4, 0.2, 0, 0]  # length must match num_grades

        # --- Clean DataFrame ---
        self.df = self.df[~self.df['Module_Code'].isin(self.sim_modules)]  # remove SIM modules
        self.df = self.df[self.df['Grade'] != 'S']  # remove S/U grades

    def run(self):
        if self.df.empty:
            print("⚠️ DataFrame is empty or None.")
            return None

        m = Model("Maximize_CGPA")
        D = m.addVars(self.sim_modules, range(self._num_grades), vtype=GRB.BINARY, name='D')

        # Objective terms
        total_units = self.df['Units'].sum() + sum(self.sim_units.values())
        
        fixed_gpa_sum = (self.df['GPA'] * self.df['Units']).sum()

        sim_gpa_sum = quicksum(
            D[i, j] * self._gpa_grades[j] * self.sim_units[i]
            for i in self.sim_modules for j in range(self._num_grades)
        )

        penalty_expr = quicksum(
            D[i, j] * self.penalties[j]
            for i in self.sim_modules for j in range(self._num_grades)
        )

        # Final objective
        m.setObjective(
            ((fixed_gpa_sum + sim_gpa_sum) / total_units) - self.lambda_penalty * penalty_expr,
            GRB.MAXIMIZE
        )

        # Constraints
        for i in self.sim_modules:
            m.addConstr(quicksum(D[i, j] for j in range(self._num_grades)) == 1)

        m.addConstr((fixed_gpa_sum + sim_gpa_sum) / total_units >= self.optimal_grade,
                    name="CGPA_min_threshold")

        m.setParam("OutputFlag", 0)
        m.optimize()

        # Debug values for frontend
        self.total_units = total_units
        self.fixed_gpa_sum = fixed_gpa_sum
        self.sim_gpa_sum = sim_gpa_sum
        self.penalty_expr = penalty_expr
        self.sim_gpa_value = sim_gpa_sum.getValue() if m.status == GRB.OPTIMAL else None
        self.penalty_value = penalty_expr.getValue() if m.status == GRB.OPTIMAL else None
        self.cgpa_value = ((fixed_gpa_sum + self.sim_gpa_value) / total_units) if m.status == GRB.OPTIMAL else None

        if m.status == GRB.OPTIMAL:
            result = {
                "selected_letters": [],
                "selected_gpas": []
            }

            for i in self.sim_modules:
                for j in range(self._num_grades):
                    if D[i, j].x > 0:
                        result['selected_gpas'].append(self._gpa_grades[j])
                        result['selected_letters'].append(self._letter_grades[j])

            return result
        else:
            return None