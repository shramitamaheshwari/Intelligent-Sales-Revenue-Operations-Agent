import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_synthetic_telemetry(num_samples=1000, churn_rate=0.10):
    np.random.seed(42)
    
    # 1. CMRR_mean (Gaussian)
    # Healthy: Mean 2500, Std 400. At Risk: Mean 2000, Std 600
    healthy_samples = int(num_samples * (1 - churn_rate))
    churn_samples = num_samples - healthy_samples
    
    cmrr_healthy = np.random.normal(loc=2500, scale=400, size=healthy_samples)
    cmrr_churn = np.random.normal(loc=1800, scale=500, size=churn_samples)
    cmrr = np.concatenate([cmrr_healthy, cmrr_churn])
    
    # 2. support_ticket_velocity (Poisson)
    # Healthy: lambda=1.2. At Risk: lambda=4.5 (frustration) or 0 (abandonment)
    st_healthy = np.random.poisson(lam=1.2, size=healthy_samples)
    st_churn_frustrated = np.random.poisson(lam=4.5, size=int(churn_samples/2))
    st_churn_abandoned = np.random.poisson(lam=0.1, size=churn_samples - int(churn_samples/2))
    st_velocity = np.concatenate([st_healthy, st_churn_frustrated, st_churn_abandoned])
    
    # 3. days_since_last_login (Exponential decay, floored to Days)
    days_healthy = np.random.exponential(scale=2, size=healthy_samples)
    days_churn = np.random.exponential(scale=14, size=churn_samples)
    days_last_login = np.concatenate([days_healthy, days_churn])
    
    labels = np.concatenate([np.zeros(healthy_samples), np.ones(churn_samples)])
    
    df = pd.DataFrame({
        'account_id': [f"ACC_{str(i).zfill(4)}" for i in range(num_samples)],
        'CMRR_mean': np.maximum(cmrr, 0),
        'support_ticket_velocity': st_velocity,
        'days_since_last_login': np.floor(days_last_login).astype(int),
        'churn_risk': labels
    })
    
    # Shuffle dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    os.makedirs(os.path.dirname('mock_datasets/telemetry.csv'), exist_ok=True)
    df.to_csv('mock_datasets/telemetry.csv', index=False)
    print(f"Generated {num_samples} records. Saved to mock_datasets/telemetry.csv")
    return df

if __name__ == "__main__":
    generate_synthetic_telemetry(num_samples=2000)
