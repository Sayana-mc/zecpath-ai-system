import subprocess
import time
from PIL import ImageGrab
import pygetwindow as gw

# Run pytest command in cmd
cmd = 'pytest day45_hr_interview_demo_finalization/tests/ -v --tb=short'
subprocess.Popen(['cmd.exe', '/c', f'title Pytest Regression Suite && {cmd} && pause'])
time.sleep(2.0)

# Capture window or screen
im = ImageGrab.grab()
im.save('real_terminal_capture.png')
print("Captured screen with terminal!")
