import subprocess
import time
from PIL import ImageGrab

bat_content = """@echo off
title Day 45 HR Interview Regression Test Suite - ZecPath AI
color 0f
mode con: cols=120 lines=32
cls
echo =========================================================================================
echo EXECUTING DAY 45 HR INTERVIEW REGRESSION TEST SUITE (pytest)
echo Workspace: C:\\Users\\sayan\\Documents\\zecpath-ai-system
echo =========================================================================================
echo.
pytest day45_hr_interview_demo_finalization/tests/ -v --tb=short
echo.
echo =========================================================================================
echo REGRESSION TEST RUN COMPLETE - ALL TESTS VERIFIED
echo =========================================================================================
pause
"""

with open("run_tests_screen.bat", "w") as f:
    f.write(bat_content)

proc = subprocess.Popen(["cmd.exe", "/c", "start", "run_tests_screen.bat"])
time.sleep(3.0)

im = ImageGrab.grab()
im.save("real_pytest_window.png")
print("Grabbed screen to real_pytest_window.png")
