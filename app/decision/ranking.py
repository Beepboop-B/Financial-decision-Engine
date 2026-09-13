from decimal import Decimal
from datetime import date
from typing import Tuple
from app.decision.models import CandidatePlan

def build_ranking_key(plan: CandidatePlan) -> Tuple:
    """
    Builds a lexicographic ranking key. Python sorts tuples element by element.
    We want to minimize the tuple, so:
    
    1. Complete by deadline (False is 0, True is 1). We want True first, so negate it.
       Wait, if we minimize, True should map to 0, False to 1.
    2. Require no spending changes. Minimize len(spending_changes).
    3. Minimize total amount paid.
    4. Start payment earlier. Minimize days from epoch or just date.
    5. Use fewer payments. Minimize len(payments).
    6. Lowest payment_option_id. Missing options (None) sort before strings, we can use empty string.
    """
    
    # 1. Complete by deadline: (False is 1, True is 0)
    # Validation must have been run to set completion_date
    if not plan.validation or not plan.validation.safe:
        # Unsafe plans sort last
        is_completed = False
    else:
        is_completed = plan.validation.completed_by_deadline
        
    c1 = 0 if is_completed else 1
    
    # 2. Number of spending changes
    c2 = len(plan.spending_changes)
    
    # 3. Total amount paid
    c3 = plan.total_paid
    
    # 4. Start date (use a default high date if none)
    c4 = plan.first_payment_date if plan.first_payment_date else date.max
    
    # 5. Number of payments
    c5 = plan.number_of_payments
    
    # 6. Payment option id
    c6 = plan.payment_option_id if plan.payment_option_id else ""
    
    key = (c1, c2, c3, c4, c5, c6)
    plan.ranking_key = key
    return key
