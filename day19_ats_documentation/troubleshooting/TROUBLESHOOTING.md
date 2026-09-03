\# ATS Troubleshooting Guide



\## 1. Python Environment Problem



\### Symptom



Python command does not work or required packages are unavailable.



\### Solution



Activate the virtual environment:



.venv\\Scripts\\Activate.ps1



Verify Python:



python --version



\---



\## 2. ModuleNotFoundError: No module named 'src'



\### Symptom



Running:



python src\\performance\_benchmark.py



may produce:



ModuleNotFoundError: No module named 'src'



\### Cause



The module uses package-style imports such as:



from src.noisy\_resume\_handler import normalize\_noisy\_text



When a file is executed directly, Python may not resolve the project package correctly.



\### Solution



Run the module from the project root using:



python -m src.performance\_benchmark



This is the recommended command for modules using src package imports.



\---



\## 3. Pytest Import Error



\### Symptom



Pytest reports:



ModuleNotFoundError: No module named 'src.noisy\_resume\_handler'



\### Solution



Make sure src contains:



\_\_init\_\_.py



Then run pytest from the Day 18 project root:



python -m pytest -v tests



\---



\## 4. Test Collection Failure



\### Symptom



Pytest shows:



collected 0 items / error



\### Possible causes



\- Incorrect working directory

\- Missing src/\_\_init\_\_.py

\- Incorrect Python import path

\- Incorrect test import



\### Solution



Navigate to the project directory:



cd C:\\Users\\sayan\\Documents\\zecpath-ai-system\\day18\_ats\_optimization



Then run:



python -m pytest -v tests



\---



\## 5. Noisy Resume Not Normalized



\### Symptom



Input contains:



Pyth0n

P0WER BI

extra spaces

multiple punctuation marks



\### Solution



Run:



python src\\noisy\_resume\_handler.py



Verify that the output contains normalized text.



\---



\## 6. Performance Benchmark Failure



\### Symptom



Performance test fails because processing exceeds the configured target.



\### Solution



Check:



\- Text normalization logic

\- Entity detection loops

\- Repeated processing

\- Unnecessary text operations

\- Excessive input size



Run:



python -m pytest -v tests



Then run:



python -m src.performance\_benchmark



\---



\## 7. Empty Resume



An empty resume should not crash the system.



The stability test verifies that empty input is handled safely.



\---



\## 8. Missing Experience



If experience information is not available, the system should safely return:



0 years



instead of crashing.



\---



\## 9. Cache Issues



If resume cache results are incorrect:



\- Check the cache directory.

\- Verify the source resume file.

\- Check cache key generation.

\- Clear old cache entries if required.



Cache location:



output/cache/



\---



\## 10. Documentation Maintenance



Whenever the ATS architecture or processing logic changes:



1\. Update ATS Technical Documentation.

2\. Update Developer Guide.

3\. Update Troubleshooting Guide.

4\. Add or update tests.

5\. Re-run the test suite.



\---



\## 11. Final Verification



Run:



python -m pytest -v tests



Then:



python -m src.performance\_benchmark



Then:



python src\\noisy\_resume\_handler.py



All commands should complete successfully.

