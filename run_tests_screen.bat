@echo off
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
