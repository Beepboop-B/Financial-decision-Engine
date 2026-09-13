import os
from datetime import date
from collections import defaultdict
from app.ingestion.csv_loader import DataLoader
from app.state.builder import build_user_state

def run_profiler():
    dataset_dir = os.path.join(os.path.dirname(__file__), 'dataset')
    loader = DataLoader(dataset_dir)
    loader.load_all()
    
    events_by_user = defaultdict(list)
    for e in loader.financial_events:
        events_by_user[e.user_id].append(e)
        
    requests_by_user = {}
    for r in loader.requests:
        requests_by_user[r.user_id] = r.request_date
        
    facts = []
    
    stats = defaultdict(int)
    stats['total_users'] = len(loader.financial_profiles)
    stats['total_raw_events'] = len(loader.financial_events)
    
    anomalies = []
    
    for profile in loader.financial_profiles:
        events = events_by_user.get(profile.user_id, [])
        as_of_date = requests_by_user.get(profile.user_id, date(2026,1,1))
        
        state = build_user_state(profile, events, facts, loader.exchange_rates, as_of_date)
        
        stats['active_events'] += len(state.active_events)
        stats['historical_events'] += len(state.historical_events)
        stats['excluded_events'] += len(state.excluded_events)
        stats['unresolved_amounts'] += len(state.unresolved_events)
        
        for ce in state.active_events + state.historical_events + state.excluded_events + state.unresolved_events:
            if ce.status.lower() == 'cancelled':
                stats['cancelled_events'] += 1
            elif ce.status.lower() == 'failed':
                stats['failed_events'] += 1
            elif ce.status.lower() == 'pending':
                stats['pending_events'] += 1
            
            if ce.superseded_by:
                stats['superseded_events'] += 1
            if ce.resolved_from:
                stats['amended_events'] += 1
                
            if ce.original_currency != ce.home_currency:
                stats['foreign_currency_events'] += 1
                
            if ce.event_type == 'recurring':
                if ce.direction == 'credit':
                    stats['recurring_income'] += 1
                else:
                    stats['recurring_expenses'] += 1
                    if ce.flexibility == 'flexible':
                        stats['flexible_expenses'] += 1
                    else:
                        stats['protected_expenses'] += 1
                        
        for trace in state.resolution_traces:
            if trace.reason == 'evidence_fact':
                stats['evidence_derived_resolutions'] += 1
                
        seen = set()
        for e in events:
            if e.event_id in seen:
                anomalies.append(f"Duplicate event ID: {e.event_id}")
            seen.add(e.event_id)
            
    print("=== PROFILING REPORT ===")
    for k, v in stats.items():
        print(f"{k}: {v}")
        
    print(f"\nAnomalies found: {len(anomalies)}")
    for a in anomalies[:10]:
        print(f" - {a}")
        
    profile_01 = next((p for p in loader.financial_profiles if p.user_id == 'user_01'), None)
    if profile_01:
        events_01 = events_by_user.get('user_01', [])
        as_of_date = requests_by_user.get('user_01', date(2026,1,1))
        state_01 = build_user_state(profile_01, events_01, facts, loader.exchange_rates, as_of_date)
        
        print("\n=== EXAMPLE STATE DUMP (user_01) ===")
        print(f"USER: {state_01.user_id}")
        print(f"AS OF DATE: {as_of_date}")
        print(f"HOME CURRENCY: {state_01.home_currency}")
        print(f"CURRENT BALANCE: {state_01.current_balance}")
        print(f"MINIMUM BALANCE: {state_01.minimum_balance_to_keep}")
        print(f"\nACTIVE EVENTS: {len(state_01.active_events)}")
        print(f"RESOLVED EVENTS TRACES: {len(state_01.resolution_traces)}")
        for trace in state_01.resolution_traces:
            print(f"  {trace.event_id} - {trace.action} due to {trace.reason} (by {trace.source_record})")

if __name__ == '__main__':
    run_profiler()
