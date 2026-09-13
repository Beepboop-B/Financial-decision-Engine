import os
import unittest
from app.ingestion.csv_loader import DataLoader

class TestIngestion(unittest.TestCase):
    def setUp(self):
        # Assumes test is run from root project directory
        self.dataset_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset')

    def test_load_all(self):
        loader = DataLoader(self.dataset_dir)
        loader.load_all()
        
        self.assertGreater(len(loader.exchange_rates), 0)
        self.assertGreater(len(loader.financial_profiles), 0)
        self.assertGreater(len(loader.financial_events), 0)
        self.assertGreater(len(loader.request_payment_options), 0)
        self.assertGreater(len(loader.requests), 0)
        self.assertGreater(len(loader.messages), 0)
        self.assertGreater(len(loader.images), 0)
        
        # Spot check a specific behavior
        # Ensure we handled blank amounts correctly (as None)
        blank_amount_events = [e for e in loader.financial_events if e.amount is None]
        self.assertGreater(len(blank_amount_events), 0, "Expected some financial events with None amount")

        # Spot check boolean parsing
        partial_allowed_requests = [r for r in loader.requests if r.allows_partial_payment is True]
        self.assertGreater(len(partial_allowed_requests), 0)

        # Spot check lists
        profile = loader.financial_profiles[0]
        self.assertIsInstance(profile.financial_priorities, list)

if __name__ == '__main__':
    unittest.main()
