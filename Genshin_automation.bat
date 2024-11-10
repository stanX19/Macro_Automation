@echo off

set "executed_dir=C:\Users\DELL\PycharmProjects\pythonProject\Macro_Automation\srcs\"

cd /d %executed_dir%

call ..\Scripts\activate.bat

set PYTHONPATH=%CD%\..\srcs;%CD%\classes;%CD%\UI;%CD%\Data_manager;%CD%\utils;%CD%\hsr;%CD%\genshin;%PYTHONPATH%

py genshin\genshin_main.py


