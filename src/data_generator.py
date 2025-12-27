import random
from faker import Faker
from datetime import datetime, timedelta
import pandas as pd

fake = Faker()

class FraudDataGenerator:
    """Generate realistic fraud detection test data"""
    
    MERCHANT_CATEGORIES = ["retail", "travel", "gambling", "crypto", "electronics"]
    COUNTRIES = ["US", "UK", "DE", "FR", "NG", "RU", "CN", "BR"]
    
    def __init__(self, fraud_ratio: float = 0.15):
        self.fraud_ratio = fraud_ratio

    def generate_transaction(self, is_fraud: bool = False) -> dict:
        """Generate a single transaction"""
        account_country = random.choice(self.COUNTRIES[:4])  # Legitimate countries
        
        if is_fraud:
            # Fraud patterns
            pattern = random.choice(['high_value_crypto', 'velocity_spike', 'gambling'])
            
            if pattern == 'high_value_crypto':
                return {
                    "transaction_id": fake.uuid4()[:8],
                    "timestamp": fake.date_time_this_month().isoformat(),
                    "transaction_amount": random.uniform(5000, 50000),
                    "transaction_velocity_24h": random.randint(1, 5),
                    "is_new_device": True,
                    "country_mismatch": random.choice([True, False]),
                    "merchant_category": "crypto",
                    "account_country": account_country,
                    "transaction_country": random.choice(self.COUNTRIES),
                    "account_age_days": random.randint(1, 30),
                }
            elif pattern == 'velocity_spike':
                tx_country = random.choice(self.COUNTRIES[4:])  # Different country
                return {
                    "transaction_id": fake.uuid4()[:8],
                    "timestamp": fake.date_time_this_month().isoformat(),
                    "transaction_amount": random.uniform(100, 2000),
                    "transaction_velocity_24h": random.randint(11, 50),
                    "is_new_device": random.choice([True, False]),
                    "country_mismatch": True,
                    "merchant_category": random.choice(self.MERCHANT_CATEGORIES),
                    "account_country": account_country,
                    "transaction_country": tx_country,
                    "account_age_days": random.randint(30, 365),
                }
            else:  # gambling
                return {
                    "transaction_id": fake.uuid4()[:8],
                    "timestamp": fake.date_time_this_month().isoformat(),
                    "transaction_amount": random.uniform(1000, 10000),
                    "transaction_velocity_24h": random.randint(1, 10),
                    "is_new_device": False,
                    "country_mismatch": False,
                    "merchant_category": "gambling",
                    "account_country": account_country,
                    "transaction_country": account_country,
                    "account_age_days": random.randint(100, 1000),
                }
        else:
            # Legitimate transaction
            return {
                "transaction_id": fake.uuid4()[:8],
                "timestamp": fake.date_time_this_month().isoformat(),
                "transaction_amount": random.uniform(10, 500),
                "transaction_velocity_24h": random.randint(1, 5),
                "is_new_device": random.choice([True, False]),
                "country_mismatch": False,
                "merchant_category": random.choice(["retail", "travel", "electronics"]),
                "account_country": account_country,
                "transaction_country": account_country,
                "account_age_days": random.randint(365, 2000),
            }

    def generate_dataset(self, n: int = 5) -> pd.DataFrame:
        """Generate a dataset with mix of fraud and legitimate transactions"""
        n_fraud = int(n * self.fraud_ratio)
        n_legit = n - n_fraud
        
        transactions = []
        transactions.extend([self.generate_transaction(is_fraud=True) for _ in range(n_fraud)])
        transactions.extend([self.generate_transaction(is_fraud=False) for _ in range(n_legit)])
        
        random.shuffle(transactions)
        return pd.DataFrame(transactions)