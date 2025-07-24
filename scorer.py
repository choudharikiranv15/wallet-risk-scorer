import pandas as pd
import numpy as np
import time
import random


class CompoundRiskScorer:
    def __init__(self, wallet_csv):
        self.wallet_df = pd.read_csv(wallet_csv)
        self.features_df = pd.DataFrame()

    def fetch_and_prepare_data(self):
        # Simulate feature extraction (replace with real on-chain API queries)
        print("⏳ Simulating transaction fetch for wallets...")
        features = []
        for wallet in self.wallet_df['wallet_id']:
            data = {
                "wallet_id": wallet,
                "total_supply": random.randint(1, 20),
                "total_borrow": random.randint(0, 15),
                "liquidations": random.randint(0, 5),
                "unique_assets": random.randint(1, 6),
                "days_since_last_txn": random.randint(1, 90)
            }
            data["borrow_supply_ratio"] = (
                data["total_borrow"] / data["total_supply"]
                if data["total_supply"] > 0 else 1
            )
            features.append(data)
            time.sleep(0.1)  # Simulate API rate limit
        self.features_df = pd.DataFrame(features)
        print("✅ Feature matrix prepared.")

    def compute_risk_scores(self):
        df = self.features_df.copy()

        # Normalize features to [0, 1]
        df['norm_borrow_ratio'] = df['borrow_supply_ratio'].clip(0, 1)
        df['norm_liquidations'] = df['liquidations'] / df['liquidations'].max()
        df['norm_recency'] = df['days_since_last_txn'] / 90
        df['norm_unique_assets'] = 1 - \
            (df['unique_assets'] / df['unique_assets'].max())

        # Compute weighted score (you can tweak weights)
        df['score'] = (
            0.4 * df['norm_borrow_ratio'] +
            0.3 * df['norm_liquidations'] +
            0.2 * df['norm_recency'] +
            0.1 * df['norm_unique_assets']
        ) * 1000

        df['score'] = df['score'].astype(int)
        self.final_df = df[['wallet_id', 'score']]
        print("✅ Risk scores computed.")

    def save_scores(self, output_file):
        self.final_df.to_csv(output_file, index=False)
        print(f"📁 Scores saved to {output_file}")
