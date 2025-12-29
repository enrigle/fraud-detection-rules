from typing import Dict, Any, List, Optional
import pandas as pd

class DataValidator:
    """Validate transaction data before processing"""

    REQUIRED_FIELDS = [
        'transaction_id',
        'transaction_amount',
        'transaction_velocity_24h',
        'merchant_category',
        'is_new_device',
        'country_mismatch',
    ]

    OPTIONAL_FIELDS = [
        'account_age_days',
        'account_country',
        'transaction_country',
        'timestamp',
    ]

    MERCHANT_CATEGORIES = ['retail', 'travel', 'gambling', 'crypto', 'electronics']

    def __init__(self):
        self.all_fields = self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS

    def validate_transaction(self, data: Dict[str, Any]) -> List[str]:
        """Validate a single transaction and return list of errors"""
        errors = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate data types and values
        if 'transaction_amount' in data:
            if not isinstance(data['transaction_amount'], (int, float)):
                errors.append("transaction_amount must be numeric")
            elif data['transaction_amount'] < 0:
                errors.append("transaction_amount cannot be negative")

        if 'transaction_velocity_24h' in data:
            if not isinstance(data['transaction_velocity_24h'], int):
                errors.append("transaction_velocity_24h must be integer")
            elif data['transaction_velocity_24h'] < 0:
                errors.append("transaction_velocity_24h cannot be negative")

        if 'merchant_category' in data:
            if data['merchant_category'] not in self.MERCHANT_CATEGORIES:
                errors.append(f"Invalid merchant_category. Must be one of: {self.MERCHANT_CATEGORIES}")

        if 'is_new_device' in data:
            if not isinstance(data['is_new_device'], bool):
                errors.append("is_new_device must be boolean (true/false)")

        if 'country_mismatch' in data:
            if not isinstance(data['country_mismatch'], bool):
                errors.append("country_mismatch must be boolean (true/false)")

        if 'account_age_days' in data:
            if not isinstance(data['account_age_days'], int):
                errors.append("account_age_days must be integer")
            elif data['account_age_days'] < 0:
                errors.append("account_age_days cannot be negative")

        return errors

    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate entire dataframe and return errors by row"""
        errors_by_row = {}

        # Check for required columns
        missing_cols = set(self.REQUIRED_FIELDS) - set(df.columns)
        if missing_cols:
            errors_by_row['schema'] = [f"Missing required columns: {missing_cols}"]
            return errors_by_row

        # Validate each row
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_errors = self.validate_transaction(row_dict)
            if row_errors:
                errors_by_row[idx] = row_errors

        return errors_by_row

    def sanitize_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and sanitize transaction data"""
        sanitized = {}

        # Copy only known fields
        for field in self.all_fields:
            if field in data:
                sanitized[field] = data[field]

        # Convert types
        if 'transaction_amount' in sanitized:
            try:
                sanitized['transaction_amount'] = float(sanitized['transaction_amount'])
            except (ValueError, TypeError):
                pass

        if 'transaction_velocity_24h' in sanitized:
            try:
                sanitized['transaction_velocity_24h'] = int(sanitized['transaction_velocity_24h'])
            except (ValueError, TypeError):
                pass

        if 'account_age_days' in sanitized:
            try:
                sanitized['account_age_days'] = int(sanitized['account_age_days'])
            except (ValueError, TypeError):
                pass

        # Convert boolean-like values
        for bool_field in ['is_new_device', 'country_mismatch']:
            if bool_field in sanitized:
                val = sanitized[bool_field]
                if isinstance(val, str):
                    sanitized[bool_field] = val.lower() in ['true', '1', 'yes', 't']
                elif isinstance(val, (int, float)):
                    sanitized[bool_field] = bool(val)

        return sanitized

    def check_required_fields(self, data: Dict[str, Any]) -> bool:
        """Quick check if all required fields are present"""
        return all(field in data for field in self.REQUIRED_FIELDS)

    def get_field_info(self) -> Dict[str, Dict[str, str]]:
        """Get metadata about available fields"""
        return {
            'transaction_id': {
                'type': 'string',
                'description': 'Unique transaction identifier',
                'required': True
            },
            'transaction_amount': {
                'type': 'number',
                'description': 'Transaction amount in dollars',
                'required': True,
                'validation': 'Must be >= 0'
            },
            'transaction_velocity_24h': {
                'type': 'integer',
                'description': 'Number of transactions in last 24 hours',
                'required': True,
                'validation': 'Must be >= 0'
            },
            'merchant_category': {
                'type': 'string',
                'description': 'Type of merchant',
                'required': True,
                'validation': f'Must be one of: {", ".join(self.MERCHANT_CATEGORIES)}'
            },
            'is_new_device': {
                'type': 'boolean',
                'description': 'Transaction from unrecognized device',
                'required': True
            },
            'country_mismatch': {
                'type': 'boolean',
                'description': 'Transaction country differs from account country',
                'required': True
            },
            'account_age_days': {
                'type': 'integer',
                'description': 'Age of account in days',
                'required': False,
                'validation': 'Must be >= 0'
            },
            'account_country': {
                'type': 'string',
                'description': 'Account registration country',
                'required': False
            },
            'transaction_country': {
                'type': 'string',
                'description': 'Transaction origin country',
                'required': False
            },
            'timestamp': {
                'type': 'string',
                'description': 'Transaction timestamp (ISO format)',
                'required': False
            }
        }
