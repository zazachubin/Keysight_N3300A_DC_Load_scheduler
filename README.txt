Source code: https://github.com/zazachubin/Keysight_N3300A_DC_Load_scheduler

# requirements:
* Build project by:
    python3 -m pip install pyinstaller
* Project libs
    python3 -m pip install pyserial
    python3 -m pip install visa
    python3 -m pip install pyvisa
    python3 -m pip install pyvisa-py
    python3 -m pip install pyqtgraph
    python3 -m pip install pyqt5

# Build program:
pyinstaller --noconfirm --onefile --windowed  .\DC_Load_scheduler.py
pyinstaller --noconfirm --onefile --windowed  .\DataPlotter.py

# Run DC_Load_scheduler program
   python .\DC_Load_scheduler.py  OR  python3 .\DC_Load_scheduler.py

# Run DataPlotter program
   python .\DataPlotter.py  OR  python3 .\DataPlotter.py


#################### Use instruction of DataPlotter ########################
* Package contains data folder where are test data logs for DataPlotter program.
* Program has open file button which activates dalog window, where are different data logs attaching buttons.
* Whenever data is loading, in program there are channel manipulation checkboxes for activate/deactivate plots.
* Program also has file generation function for produce one file from five files.
* progrme calculates temperature cycles min-max difference and plots on the graph.


