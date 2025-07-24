from scorer import CompoundRiskScorer


if __name__ == "__main__":
    scorer = CompoundRiskScorer(wallet_csv="wallets.csv")
    scorer.fetch_and_prepare_data()
    scorer.compute_risk_scores()
    scorer.save_scores("wallet_risk_scores.csv")
