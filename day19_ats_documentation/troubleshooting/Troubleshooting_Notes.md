\# ATS Troubleshooting Notes



\## 1. Python ModuleNotFoundError



\### Error



ModuleNotFoundError: No module named 'src'



\### Cause



The Python module is being executed from an incorrect directory or using an execution method that does not correctly resolve the project package.



\### Solution



Run the module from the project root:



python -m src.performance\_benchmark



Instead of:



python src\\performance\_benchmark.py



Make sure the current directory is the project root.



\---



\## 2. Pytest Cannot Find Tests



\### Error



ERROR: file or directory not found: tests



\### Cause



The command was executed from a directory that does not contain the tests folder.



\### Solution



Navigate to the correct project directory first.



Example:



cd C:\\Users\\sayan\\Documents\\zecpath-ai-system\\day18\_ats\_optimization



Then run:



python -m pytest -v tests



\---



\## 3. File Not Found



\### Error



can't open file ... noisy\_resume\_handler.py



\### Cause



The requested source file does not exist in the current project directory.



\### Solution



Check the project structure:



Get-ChildItem -Recurse



Then navigate to the correct project directory.



\---



\## 4. Pytest Import Error



If pytest cannot import a module from src:



1\. Confirm src contains \_\_init\_\_.py.

2\. Confirm the source file exists.

3\. Run pytest from the project root.

4\. Use:



python -m pytest -v tests



\---



\## 5. Noisy Resume Processing



If noisy text is not normalized correctly:



\- Check the normalization rules.

\- Verify the input string.

\- Confirm the normalization function is being imported correctly.

\- Run the noisy resume handler directly.



Example:



python src\\noisy\_resume\_handler.py



\---



\## 6. Performance Benchmark



Use:



python -m src.performance\_benchmark



The benchmark reports:



\- Text normalization time

\- Entity detection time

\- Peak memory usage

\- Performance check status



\---



\## 7. Test Verification



Run:



python -m pytest -v tests



A successful run should display:



7 passed



\---



\## 8. General Debugging Checklist



Before running the ATS:



1\. Activate the virtual environment.

2\. Confirm the current directory.

3\. Check the project structure.

4\. Confirm required files exist.

5\. Run unit tests.

6\. Run performance benchmark.

7\. Check generated output files.

8\. Review errors before continuing.

