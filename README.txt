Source code: https://github.com/zazachubin/Keysight_N3300A_DC_Load_scheduler

# requirements:
* Build project by:
    python3 -m pip install pyinstaller
* Project libs
    python3 -m pip install pyserial
    python3 -m pip install visa
    python3 -m pip install pyvisa
    python3 -m pip install pyqt5

# Build program:
pyinstaller --noconfirm --onefile --windowed  .\DC_Load_scheduler.py