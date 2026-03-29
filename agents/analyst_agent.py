from crewai import Agent
import pandas as pd

class AnalystAgentBuilder:
    @staticmethod
    def build_agent():
        return Agent(
            role='RevOps Intelligence Analyst',
            goal='Detect competitor mentions and churn signals in client telemetry and emails.',
            backstory='An analytical engine trained on B2B SaaS usage metrics and BERT sentiment models. You are highly detail-oriented.',
            verbose=True,
            llm="groq/llama-3.1-8b-instant"
        )

# Pipeline structure Mock
class ChurnScoringPipeline:
    def __init__(self):
        from sklearn.ensemble import RandomForestClassifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def train(self, data_path: str):
        df = pd.read_csv(data_path)
        X = df[['CMRR_mean', 'support_ticket_velocity', 'days_since_last_login']]
        y = df['churn_risk']
        self.model.fit(X, y)
        print("Model Trained.")
        
    def predict_risk(self, features: list):
        # features format: [CMRR, support, days_last_login]
        # Wrap in DataFrame with the exact column names used during training
        # to avoid sklearn feature name mismatch warnings
        import pandas as pd
        X = pd.DataFrame([features], columns=['CMRR_mean', 'support_ticket_velocity', 'days_since_last_login'])
        return self.model.predict_proba(X)[0][1]  # Probability of churn
