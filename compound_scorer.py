import requests
import csv
from datetime import datetime

GRAPH_API = "https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2"


def run_query(query):
    response = requests.post(GRAPH_API, json={'query': query})
    if response.status_code == 200:
        return response.json()['data']
    else:
        raise Exception(
            f"Query failed with status code {response.status_code}")


def fetch_wallet_data(wallet):
    wallet = wallet.lower()
    query = f"""
    {{
      account(id: "{wallet}") {{
        id
        tokens {{
          symbol
          supplyBalanceUnderlying
          borrowBalanceUnderlying
        }}
        borrowEvents(first: 100) {{
          amount
          blockTimestamp
        }}
        repayEvents(first: 100) {{
          amount
          blockTimestamp
        }}
        liquidationEvents(first: 100) {{
          amountRepaid
          seizedCollateral
          blockTimestamp
        }}
      }}
    }}
    """
    return run_query(query)


def calculate_risk(wallet_data):
    if not wallet_data or not wallet_data.get('account'):
        return 1000  # Maximum risk if no data

    account = wallet_data['account']
    borrow_events = account.get('borrowEvents', [])
    repay_events = account.get('repayEvents', [])
    liquidations = account.get('liquidationEvents', [])

    total_borrowed = sum(float(e['amount']) for e in borrow_events)
    total_repaid = sum(float(e['amount']) for e in repay_events)
    liquidation_count = len(liquidations)

    latest_ts = 0
    for e in borrow_events + repay_events:
        ts = int(e['blockTimestamp'])
        if ts > latest_ts:
            latest_ts = ts

    now = int(datetime.utcnow().timestamp())
    days_inactive = (now - latest_ts) / 86400 if latest_ts > 0 else 365

    repayment_ratio = total_repaid / total_borrowed if total_borrowed > 0 else 1
    ltv = (total_borrowed / (total_borrowed + total_repaid)
           ) if (total_borrowed + total_repaid) > 0 else 0.5

    # Scoring Formula
    score = 1000
    score -= int(ltv * 400)
    score -= int((1 - repayment_ratio) * 300)
    score -= int(liquidation_count * 50)
    score -= int(min(days_inactive, 365) / 365 * 250)

    return max(score, 0)


def process_wallets(input_csv, output_csv):
    with open(input_csv, 'r') as infile:
        reader = csv.reader(infile)
        headers = next(reader)
        wallets = [row[0].strip() for row in reader]

    results = []

    for wallet in wallets:
        print(f"Fetching data for {wallet}")
        try:
            data = fetch_wallet_data(wallet)
            score = calculate_risk(data)
            results.append([wallet, score])
        except Exception as e:
            print(f"Error processing {wallet}: {e}")
            results.append([wallet, "Error"])

    with open(output_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Wallet Address', 'Risk Score'])
        writer.writerows(results)


if __name__ == "__main__":
    process_wallets("wallets.csv", "wallet_risk_scores.csv")
