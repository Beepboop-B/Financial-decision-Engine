# SUBMISSION ARTIFACTS

1. code.zip
   size: 132003 bytes
   sha256: 6322BE5945B5E2C3393DC22C3AEB75855FAFE8FF77451E87989D7E768EB51A46

2. output.csv
   rows: 250 (251 including header)
   size: 59570 bytes
   sha256: 79ED4F3E870ED1B9DD0B10012A555E43C5D1C3DB8D6AA8124A7F1D1C50FC7D70

3. chat transcript
   path: log.txt
   size: 866332 bytes
   sha256: 52C098D78EDDA24C44CE4F3B8EBFEA90AAC9FC5366D6B99EDC811E1E8D501556

# VALIDATION

- tests: PASSED (19/19 deterministic engine tests)
- API tests: PASSED (11/11 FastApi integration tests)
- frontend build: PASSED (Vite production build successful)
- output validator: PASSED (app.pipeline.validator completed successfully)
- secrets scan: PASSED (No GEMINI_API_KEY, AIza, sk-, SECRET, PASSWORD, or TOKEN found in code.zip)
- dataset exclusion: PASSED (`dataset/` safely excluded from code.zip)
- obsolete model scan: PASSED (Updated to gemini-3.5-flash-lite. No gemini-1.5-flash in code.zip)

# REAL MODEL STATUS:
NOT COMPLETED — CREDENTIALS NOT AVAILABLE
Zero real LLM tokens were consumed in this generation. The engine safely fell back to the `DummyLLMClient`, generating the exact mathematical baseline predictions offline. 

# KNOWN LIMITATIONS:
- Due to the offline nature of the final output, evidence from unstructured text (such as hidden discounts in messages or invoices) was simulated deterministically instead of extracted via a real LLM prompt. Actual behavior will vary if real API keys are introduced.
- The UI handles "Demo Mode" manually. To hook this up to a live multi-user setup, authentication routes (e.g., JWT) would need to be provisioned over the existing REST routes.
