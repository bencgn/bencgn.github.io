@echo off
cd /d "%~dp0\.."
python publiccontent\create_article.py --gui
pause
