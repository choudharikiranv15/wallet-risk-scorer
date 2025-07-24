# 🧠 Wallet Risk Scorer

This project evaluates the risk profile of Ethereum wallets by analyzing their transaction history from the Compound V2 protocol and generating a risk score between 0 and 1000 for each wallet.

---

## 📌 Problem Statement

You are provided with a list of Ethereum wallet addresses.

### Your task:

1. **Fetch Transaction History:**
   - Retrieve on-chain transaction data for each wallet from the Compound V2 or V3 protocol.
2. **Data Preparation:**
   - Preprocess this data into meaningful patterns that can reflect a wallet's activity.
3. **Risk Scoring:**
   - Develop a scoring system to evaluate the risk level of each wallet (0 = high risk, 1000 = low risk).
4. **Deliverable:**
   - A CSV file:
     ```csv
     wallet_id,score
     0xfaa0768bde629806739c3a4620656c5d26f44ef2,732
     ```

---

## 📥 Data Collection Method

We collect on-chain wallet activity data using the [Covalent API](https://www.covalenthq.com/docs/api/) by querying:

- `/v1/1/address/{wallet_address}/transactions_v2/`  
  This returns recent transactions (e.g., deposits, borrows, repayments, etc.) for the given wallet on the Ethereum mainnet.

Each transaction includes:

- Transaction type (transfer)
- Value transferred
- Gas spent
- From / To address

---

## 📁 Project Structure

````bash
wallet-risk-scorer/
├── main.py                  # Entry-point script to compute risk scores
├── compound_scorer.py       # Core logic for transaction fetching, feature engineering, and scoring
├── scorer.py                # Utility functions for min-max normalization
├── data/
│   └── wallets.txt          # Input file containing 100 wallet addresses
├── outputs/
│   └── risk_scores.csv      # Output file with risk scores for each wallet
├── README.md                # This file

## 🧮 Feature Selection

Due to the limitations of the Covalent endpoint and absence of Compound-specific data (e.g., `cTokens`, liquidation history), we focus on:

| Feature               | Description                                                   |
| --------------------- | ------------------------------------------------------------- |
| `num_transactions`    | Number of transactions fetched from Covalent                  |
| `total_gas_spent`     | Sum of all gas fees in ETH for the wallet                     |
| `avg_tx_value`        | Average transaction value in ETH                              |
| `high_value_tx_count` | Count of transactions over a defined threshold (e.g., >1 ETH) |
| `activity_score`      | Weighted score derived from activity and gas usage            |

> 🔍 Note: True lending protocol data (e.g., from Compound's subgraph) was not queried due to time or resource constraints. Therefore, these features are general activity indicators, not protocol-specific behaviors like borrow vs. supply ratio or liquidation count.

---

## 🧪 Feature Engineering

We applied the following simple transformations:

- Normalize `num_transactions`, `total_gas_spent`, and `avg_tx_value` on a [0, 1] scale
- Apply a linear weighted formula:

```python
risk_score = (
    0.4 * norm_tx_count +
    0.3 * norm_gas_spent +
    0.3 * norm_avg_value
) * 1000
````

⚖️ Risk Scoring Logic
The final score is calculated using:

python
Copy
Edit
final_score = int(min(1000, max(0, weighted_score)))
The logic assumes that:

More transactions indicate reliability and usage history.

Higher gas usage indicates more engagement with smart contracts.

Higher average value reflects stronger capital involvement.

Inactive or empty wallets receive scores near 0.

📤 Output
The final result is a CSV file with scores for each wallet, like:

csv
Copy
Edit
wallet_id,score
0xfaa0768bde629806739c3a4620656c5d26f44ef2,732
0xabc123...,590
...
⚠️ Limitations
No direct Compound protocol data (e.g., liquidation history, borrow ratio)

Covalent limits the amount of data (1000 tx max)

Some wallets may have very few transactions or none at all

The model is activity-based, not protocol-behavior-based

📈 Improvements
Integrate Compound V2/V3 Subgraph API for richer protocol-specific data

Add credit delegation, liquidation history, and collateral factor

Use machine learning models with labeled risk outcomes if data available

📬 Contact
For questions, contact Kiran Choudhari
