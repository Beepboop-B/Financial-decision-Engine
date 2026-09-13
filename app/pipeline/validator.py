import csv
import json
from decimal import Decimal

def validate_output():
    required_columns = [
        "request_id", "amount_safe_to_pay", "affordability_status", 
        "recommended_payment_method", "payment_plan", 
        "earliest_date_for_full_payment", "spending_changes_needed", 
        "decision_explanation"
    ]
    
    with open('evaluation/output_baseline.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        if reader.fieldnames != required_columns:
            print("ERROR: Columns do not match exactly.")
            return False
            
        rows = list(reader)
        
    if len(rows) != 250:
        print(f"ERROR: Expected 250 rows, got {len(rows)}")
        return False
        
    req_ids = set()
    for i, row in enumerate(rows):
        if row['request_id'] in req_ids:
            print(f"ERROR: Duplicate request_id {row['request_id']}")
            return False
        req_ids.add(row['request_id'])
        
        amt = Decimal(row['amount_safe_to_pay'])
        if amt < 0:
            print(f"ERROR: Negative amount safe {amt}")
            return False
            
        status = row['affordability_status']
        if status not in ["affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"]:
            print(f"ERROR: Invalid status {status}")
            return False
            
        plan = json.loads(row['payment_plan'])
        if not isinstance(plan, list):
            print("ERROR: Invalid payment plan structure")
            return False
            
        if not row['decision_explanation']:
            print("ERROR: Missing explanation")
            return False
            
    print("OUTPUT VALIDATION PASSED.")
    return True

if __name__ == '__main__':
    validate_output()
