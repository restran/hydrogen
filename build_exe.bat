pyinstaller --onefile --windowed --exclude-module=django --add-data="static;static" --add-data="templates;templates" --icon=assets/icon.ico main.py 
pause