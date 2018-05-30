pyinstaller --onefile --windowed --exclude-module=django --add-data="static;static" --add-data="ca;ca" --add-data="certs;certs" --add-data="templates;templates" --icon=assets/icon.ico main.py
pause