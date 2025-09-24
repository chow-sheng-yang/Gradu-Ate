from utils import *
import torch
import torch.nn.functional as F
import pandas as pd
from Recommender_Embeddings import *

class Recommender:
    '''
        It can store the following:
        - user's career tags
        - user's CFTV
        - career tag embeddings / normalised career tag embeddings
        - module description embeddings / normalised description embeddings
        - number of career tags
        - number of modules in recommendation basket
        - module x career tag similarity matrix
        - variance tuning lambda hyperparameter
        - device
        - top R modules
    '''
    def __init__(self, lambda_reg=0.5, device=None):

        self.CE_df = load_Career_Tag_embeddings()                           # CE = Career Embeddings    
        self.ME_df = load_Module_Description_embeddings()                   # ME = Module Description Embeddings
        self.CE = torch.tensor(self.CE_df.values, dtype=torch.float32)
        self.ME= torch.tensor(self.ME_df.values, dtype=torch.float32)
        self.career_tags_basket = list(careers_df['Career'].unique())       # career_tags = Careers in career tag basket
        self.K = len(careers_df['Career'].unique())                         # K = Number of Career-Tags
        self.M = len(modules_df['Module_Code'].unique())                    # M = Number of Modules in recommendation basket

        self.CE_norm = F.normalize(self.CE, p=2, dim=1)                     # CE_norm = Normalized(CE)
        self.ME_norm = F.normalize(self.ME, p=2, dim=1)                     # ME_norm = Normalized(ME)

        self.user_career_tags = None
        self.CFTV = None
        self.top_R_modules = None

        if device is None:
            device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.device = device                                                # device = device

        self.lambda_reg = lambda_reg                                        # lambda_reg = Lambda used for variance-adjustment
        
        self.sim = torch.mm(self.ME_norm, self.CE_norm.T).to(self.device)   # sim = Module x Career-Tag Similarity Matrix
    
    def fit(self, user_career_tags, user_career_ranking=None):
        self.user_career_tags = user_career_tags                            # user_career_tags = User's Selected Career Tags of Interest
        self.CFTV = torch.zeros(self.K, dtype=torch.float32, device=self.device)                # CFTV = User's Career-Tag Feature Vector
        for tag, w in user_career_ranking.items():
            idx = self.career_tags_basket.index(tag)
            self.CFTV[idx] = w
    
    def recommend_modules(self, R, return_modcodes=True):
        scores = torch.matmul(self.sim, self.CFTV)

        D = self.sim - scores.unsqueeze(1)
        V = torch.matmul(D * D, self.CFTV)

        final = scores - self.lambda_reg * V
        final = (final - final.min()) / (final.max() - final.min())
        
        if R <= self.M:
            final_top_R = pd.Series(final.cpu().numpy()).sort_values(ascending=False).head(R)
            final_top_R_idx, final_top_R_scores = final_top_R.index, final_top_R.values
            self.top_R_modules = modules_df.iloc[final_top_R_idx]           # top_R_modules = Top R Modules Dataframe
            self.top_R_modules['final_score'] = final_top_R_scores
            self.top_R_modules['rank'] = self.top_R_modules['final_score'].rank(ascending=False, method="min")
            if return_modcodes:
                return self.top_R_modules['Module_Code']
            return self.top_R_modules
        else:
            return None
    
    def return_CAV_dataframe(self, top_R_modules:list):
        data = {}
        sim_df = pd.DataFrame(self.sim.cpu().numpy(),
                              index=modules_df['Module_Code'].tolist(),
                              columns=careers_df['Career'].tolist())
        for idx, mod in enumerate(top_R_modules):
            CAV = sim_df.loc[mod, self.user_career_tags]
            data[mod] = {}
            for career_tag in self.user_career_tags:
                data[mod][career_tag] = CAV.loc[career_tag]
        
        data = pd.DataFrame(data).T
        data.reset_index(inplace=True)
        data.rename(columns={"index" : "Module_Code"}, inplace=True)
        data = data.merge(self.top_R_modules, how='left', on="Module_Code")
        return data[['Module_Code']+self.user_career_tags+['final_score', 'rank']]
    
