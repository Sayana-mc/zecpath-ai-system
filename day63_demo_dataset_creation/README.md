# Day 63: Demo Dataset Creation

Build a JSON dataset by joining the sample resumes with their available
screening outputs and job descriptions. Candidates without a screening output
are included with `null` screening and job fields. This is demo data only, not a
hiring decision.

Run these commands from this directory:

```powershell
python -m src.main
python -m unittest discover -s tests -v
```

The builder writes `output/demo_dataset.json`. Input paths are resolved relative
to the source files rather than to the shell's current working directory.
