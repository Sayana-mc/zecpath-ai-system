\# ATS Developer Guide



\## 1. Purpose



This guide explains how a developer can understand, run, test, maintain, and extend the ATS system.



\---



\## 2. Project Structure



The ATS project is organized into multiple development stages.



Important modules include:



\- Resume extraction

\- Resume normalization

\- Entity detection

\- Candidate ranking

\- ATS testing

\- Performance optimization



The Day 18 optimization project contains:



src/

&#x20;   entity\_optimizer.py

&#x20;   memory\_monitor.py

&#x20;   noisy\_resume\_handler.py

&#x20;   optimized\_extractor.py

&#x20;   performance\_benchmark.py

&#x20;   prompt\_optimizer.py

&#x20;   resume\_cache.py



tests/

&#x20;   test\_performance.py

&#x20;   test\_stability.py



output/

&#x20;   performance\_results.json



\---



\## 3. Environment



The project uses Python.



A virtual environment is used for dependency isolation.



Activate the environment using:



.venv\\Scripts\\Activate.ps1



\---



\## 4. Running the Noisy Resume Handler



Run:



python src\\noisy\_resume\_handler.py



The module demonstrates how noisy resume text is normalized.



Example:



Input:



Pyth0n Developer!!!

Skilled in SQL!!!

P0WER BI



Output:



Python Developer! Skilled in SQL! Power BI



\---



\## 5. Running the Performance Benchmark



Run the benchmark as a Python module:



python -m src.performance\_benchmark



The benchmark measures:



\- Text normalization time

\- Entity detection time

\- Peak memory usage



Example result:



Text normalization time : 0.005928 seconds

Entity detection time   : 0.000243 seconds

Peak memory usage       : 912.57 KB



\---



\## 6. Running Tests



Run:



python -m pytest -v tests



The Day 18 test suite contains 7 tests.



Expected result:



7 passed



The tests cover:



\- Text normalization speed

\- Entity detection speed

\- Empty resume

\- Noisy text

\- Skill detection

\- Experience detection

\- Missing experience



\---



\## 7. Test Development



Tests are located inside:



tests/



Performance tests:



tests/test\_performance.py



Stability tests:



tests/test\_stability.py



Developers should add tests whenever new functionality is introduced.



\---



\## 8. Adding a New Feature



Recommended development process:



1\. Identify the required feature.

2\. Create or update the relevant module.

3\. Add unit tests.

4\. Run the test suite.

5\. Run performance benchmarks if required.

6\. Review the output.

7\. Update technical documentation.

8\. Update troubleshooting notes.



\---



\## 9. Modifying Text Normalization



Text normalization is implemented in:



src/noisy\_resume\_handler.py



Changes should be tested using:



python -m pytest -v tests



The noisy text test should continue to pass.



\---



\## 10. Modifying Entity Detection



Entity detection is implemented in:



src/entity\_optimizer.py



After modifying the module, test:



python -m pytest -v tests



Important functionality includes:



\- Skill detection

\- Experience detection



\---



\## 11. Modifying Prompt Optimization



Prompt optimization is implemented in:



src/prompt\_optimizer.py



Important resume sections are:



\- Summary

\- Skills

\- Experience

\- Education

\- Projects

\- Certifications



The maximum text length can be controlled using the text limiting functionality.



\---



\## 12. Resume Cache



Caching is implemented in:



src/resume\_cache.py



The cache uses SHA-256 hashing of resume file content.



Cached files are stored under:



output/cache/



The cache should be used when repeated processing of identical resume files occurs.



\---



\## 13. Performance Monitoring



Performance benchmarking is implemented in:



src/performance\_benchmark.py



Performance should be measured after major optimization changes.



Important measurements:



\- Text processing time

\- Entity detection time

\- Memory usage



\---



\## 14. Stability Requirements



The ATS should continue to work when:



\- Resume text is empty.

\- Resume text contains noisy characters.

\- Experience information is missing.

\- Known skills are present.

\- Resume formatting is inconsistent.



\---



\## 15. Coding Guidelines



Developers should:



\- Keep modules focused on a single responsibility.

\- Use meaningful function names.

\- Add tests for new functionality.

\- Avoid unnecessary processing.

\- Handle missing values safely.

\- Keep documentation updated.

\- Use clear error messages.

\- Avoid hard-coded assumptions where possible.



\---



\## 16. Maintenance Checklist



Before committing changes:



\[ ] Run all tests.



\[ ] Check for test failures.



\[ ] Run the performance benchmark when applicable.



\[ ] Verify output files.



\[ ] Check noisy resume handling.



\[ ] Check entity detection.



\[ ] Update documentation.



\[ ] Update troubleshooting notes.



\---



\## 17. Recommended Development Workflow



Feature Request

&#x20;       |

&#x20;       v

Implementation

&#x20;       |

&#x20;       v

Unit Tests

&#x20;       |

&#x20;       v

Performance Test

&#x20;       |

&#x20;       v

Stability Test

&#x20;       |

&#x20;       v

Documentation Update

&#x20;       |

&#x20;       v

Code Review

&#x20;       |

&#x20;       v

Final Integration



\---



\## 18. Conclusion



The developer guide provides the basic procedures required to operate and extend the ATS.



Developers should follow the testing and documentation workflow before integrating changes into the system.

