@echo off
echo [SETUP] Menginstall library...
pip install -r requirements.txt

echo.
echo [SETUP] Memastikan Template...
python create_templates.py

echo.
echo [START] Menjalankan Secretary Swarm (Modular)...
python main.py

echo.
pause
