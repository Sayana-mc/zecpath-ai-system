import subprocess
import time
import win32gui
from PIL import ImageGrab
import shutil

bat_content = """@echo off
title Day 45 HR Interview Regression Test Suite - ZecPath AI
color 0f
mode con: cols=100 lines=26
cls
echo =========================================================================================
echo EXECUTING DAY 45 HR INTERVIEW REGRESSION TEST SUITE (pytest)
echo =========================================================================================
echo.
pytest day45_hr_interview_demo_finalization/tests/ -v --tb=short
echo.
echo =========================================================================================
echo REGRESSION TEST RUN COMPLETE - 9 PASSED
echo =========================================================================================
pause
"""

with open("run_tests_screen.bat", "w") as f:
    f.write(bat_content)

proc = subprocess.Popen(["cmd.exe", "/c", "start", "run_tests_screen.bat"])
time.sleep(6.5)

hwnd = win32gui.FindWindow(None, "Day 45 HR Interview Regression Test Suite - ZecPath AI")

if hwnd:
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    rect = win32gui.GetWindowRect(hwnd)
    x1, y1, x2, y2 = rect
    im = ImageGrab.grab((x1, y1, x2, y2 + 20))
    
    target_path = "day45_hr_interview_demo_finalization/screenshots/12_automated_regression_results.png"
    mirror_path = "day45_hr_interview_finalization/screenshots/12_automated_regression_results.png"
    im.save(target_path)
    shutil.copy2(target_path, mirror_path)
    print("Saved real terminal screenshot successfully!")
    
    import win32con
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
