@echo off

set "executed_dir=%~dp0\srcs\"

cd /d %executed_dir%

call ..\.venv\Scripts\activate.bat

set PYTHONPATH=%CD%\..\srcs;%CD%\classes;%CD%\UI;%CD%\Data_manager;%CD%\utils;%CD%\hsr;%CD%\hsr\generate_templates;%PYTHONPATH%

py hsr\star_rail_main.py


