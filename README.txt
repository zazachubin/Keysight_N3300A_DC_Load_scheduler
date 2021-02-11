Source code: https://github.com/zazachubin/Keysight_N3300A_DC_Load_scheduler

# requirements:
* Build project by:
    python3 -m pip install pyinstaller
* Project libs
    python3 -m pip install pyqt5
    python3 -m pip install pyvisa

# Build program:
pyinstaller --noconfirm --onefile --windowed  .\DC_Load_scheduler.py