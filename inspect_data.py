"""Deep data investigation for Phase 2/2B"""
import os, csv
from collections import Counter, defaultdict
from app.ingestion.csv_loader import DataLoader

loader = DataLoader('dataset')
loader.load_all()

print("=== EVENT TYPES ===")
print(Counter(e.event_type for e in loader.financial_events))

print("\n=== STATUSES ===")
print(Counter(e.status for e in loader.financial_events))

print("\n=== DIRECTIONS ===")
print(Counter(e.direction for e in loader.financial_events))

print("\n=== FLEXIBILITY VALUES ===")
print(Counter(e.flexibility for e in loader.financial_events))

print("\n=== CATEGORIES (top 20) ===")
print(Counter(e.category for e in loader.financial_events).most_common(20))

print("\n=== CURRENCIES ===")
print(Counter(e.currency for e in loader.financial_events))

print("\n=== EVENTS WITH BLANK AMOUNT ===")
blank = [e for e in loader.financial_events if e.amount is None]
print(f"Count: {len(blank)}")
for b in blank:
    print(f"  {b.event_id} user={b.user_id} type={b.event_type} cat={b.category} status={b.status}")

print("\n=== LINKED EVENTS ===")
linked = [e for e in loader.financial_events if e.linked_event_id]
print(f"Count: {len(linked)}")
for l in linked[:10]:
    print(f"  {l.event_id} -> {l.linked_event_id} type={l.event_type} status={l.status}")

print("\n=== IMAGES ===")
for img in loader.images:
    print(f"  {img.image_id} user={img.user_id} req={img.request_id} event={img.related_event_id}")

print("\n=== FLEXIBILITY BY EVENT_TYPE ===")
flex_by_type = defaultdict(lambda: Counter())
for e in loader.financial_events:
    flex_by_type[e.event_type][e.flexibility] += 1
for t, c in flex_by_type.items():
    print(f"  {t}: {dict(c)}")
