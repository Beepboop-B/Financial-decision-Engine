from app.decision.models import Decision

def generate_explanation(decision: Decision) -> str:
    """
    Generates a deterministic explanation from the Decision object.
    Never invents numbers.
    """
    if decision.affordability_status == "affordable_now":
        return f"The full requested amount of {decision.amount_safe_to_pay} is safe to pay today without any spending changes. Recommended method is {decision.recommended_payment_method}."
        
    elif decision.affordability_status == "affordable_later":
        return f"The request is not safe to pay today. However, the full amount will become safe to pay on {decision.earliest_date_for_full_payment}. Recommended method is {decision.recommended_payment_method}."
        
    elif decision.affordability_status == "affordable_with_plan":
        changes = ", ".join(decision.spending_changes_needed)
        if decision.recommended_payment_method == "partial_payment":
            return f"The max safe amount today is {decision.amount_safe_to_pay}. By making spending changes ({changes}), you can pay the remainder by {decision.earliest_date_for_full_payment}. Recommended method is partial_payment."
        elif decision.recommended_payment_method == "installments":
            plan = decision.selected_candidate
            return f"The max safe upfront amount is {decision.amount_safe_to_pay}. By making spending changes ({changes}), you can afford the {plan.number_of_payments}-payment installment plan."
        else:
            return f"The max safe baseline amount is {decision.amount_safe_to_pay}. By making spending changes ({changes}), you can afford the {decision.recommended_payment_method} plan."
            
    else: # not_affordable
        return f"The safe amount is {decision.amount_safe_to_pay}. The request is not affordable within 90 days under any acceptable payment plan."
