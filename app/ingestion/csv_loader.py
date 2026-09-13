import csv
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict
from app.models.schemas import (
    ExchangeRate, FinancialProfile, FinancialEvent,
    RequestPaymentOption, UserRequest, Message, Image
)

def parse_date(date_str: str) -> Optional[date]:
    if not date_str:
        return None
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()

def parse_decimal(dec_str: str) -> Optional[Decimal]:
    if not dec_str:
        return None
    return Decimal(dec_str.strip())

def parse_int(int_str: str) -> Optional[int]:
    if not int_str:
        return None
    return int(int_str.strip())

def parse_bool(bool_str: str) -> bool:
    if not bool_str:
        return False
    return bool_str.strip().lower() == "true"

def parse_list(list_str: str) -> List[str]:
    if not list_str:
        return []
    return [x.strip() for x in list_str.split('|') if x.strip()]

def load_exchange_rates(filepath: str) -> List[ExchangeRate]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(ExchangeRate(
                rate_date=parse_date(row['rate_date']),
                from_currency=row['from_currency'],
                to_currency=row['to_currency'],
                rate=parse_decimal(row['rate'])
            ))
    return results

def load_financial_profiles(filepath: str) -> List[FinancialProfile]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(FinancialProfile(
                user_id=row['user_id'],
                home_currency=row['home_currency'],
                current_available_balance=parse_decimal(row['current_available_balance']),
                minimum_balance_to_keep=parse_decimal(row['minimum_balance_to_keep']),
                financial_priorities=parse_list(row['financial_priorities']),
                expense_categories_to_protect=parse_list(row['expense_categories_to_protect']),
                expense_categories_user_is_willing_to_reduce=parse_list(row['expense_categories_user_is_willing_to_reduce']),
                expense_categories_user_is_willing_to_stop=parse_list(row['expense_categories_user_is_willing_to_stop']),
                payment_methods_user_will_consider=parse_list(row['payment_methods_user_will_consider']),
                max_installment_months=parse_int(row.get('max_installment_months'))
            ))
    return results

def load_financial_events(filepath: str) -> List[FinancialEvent]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(FinancialEvent(
                event_id=row['event_id'],
                user_id=row['user_id'],
                event_type=row['event_type'],
                description=row['description'],
                category=row['category'],
                direction=row['direction'],
                amount=parse_decimal(row['amount']) if row['amount'].strip() else None,
                currency=row['currency'],
                event_date=parse_date(row['event_date']),
                settlement_date=parse_date(row['settlement_date']),
                status=row['status'],
                linked_event_id=row.get('linked_event_id') or None,
                flexibility=row['flexibility'],
                minimum_allowed_amount=parse_decimal(row.get('minimum_allowed_amount'))
            ))
    return results

def load_request_payment_options(filepath: str) -> List[RequestPaymentOption]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(RequestPaymentOption(
                payment_option_id=row['payment_option_id'],
                request_id=row['request_id'],
                payment_method=row['payment_method'],
                payment_amount=parse_decimal(row['payment_amount']),
                number_of_payments=parse_int(row['number_of_payments']),
                first_payment_date=parse_date(row['first_payment_date']),
                payment_frequency_days=parse_int(row.get('payment_frequency_days')),
                financing_fee=parse_decimal(row['financing_fee']),
                total_payable_amount=parse_decimal(row['total_payable_amount'])
            ))
    return results

def load_user_requests(filepath: str) -> List[UserRequest]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(UserRequest(
                request_id=row['request_id'],
                user_id=row['user_id'],
                request_date=parse_date(row['request_date']),
                request_type=row['request_type'],
                requested_amount=parse_decimal(row['requested_amount']),
                desired_completion_date=parse_date(row['desired_completion_date']),
                allows_partial_payment=parse_bool(row['allows_partial_payment']),
                request_text=row['request_text']
            ))
    return results

def load_messages(filepath: str) -> List[Message]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(Message(
                message_id=row['message_id'],
                user_id=row['user_id'],
                request_id=row.get('request_id') or None,
                related_event_id=row.get('related_event_id') or None,
                sent_at=row['sent_at'],
                source_type=row['source_type'],
                message_text=row['message_text']
            ))
    return results

def load_images(filepath: str) -> List[Image]:
    results = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(Image(
                image_id=row['image_id'],
                user_id=row['user_id'],
                request_id=row.get('request_id') or None,
                related_event_id=row.get('related_event_id') or None
            ))
    return results

class DataLoader:
    def __init__(self, dataset_dir: str):
        import os
        self.dataset_dir = dataset_dir
        
    def load_all(self):
        import os
        self.exchange_rates = load_exchange_rates(os.path.join(self.dataset_dir, 'exchange_rates.csv'))
        self.financial_profiles = load_financial_profiles(os.path.join(self.dataset_dir, 'financial_profiles.csv'))
        self.financial_events = load_financial_events(os.path.join(self.dataset_dir, 'financial_events.csv'))
        self.request_payment_options = load_request_payment_options(os.path.join(self.dataset_dir, 'request_payment_options.csv'))
        self.requests = load_user_requests(os.path.join(self.dataset_dir, 'requests.csv'))
        self.messages = load_messages(os.path.join(self.dataset_dir, 'messages.csv'))
        self.images = load_images(os.path.join(self.dataset_dir, 'images.csv'))
        return self
