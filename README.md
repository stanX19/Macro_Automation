# Macro_Automation

# setup

```commandline
git clone https://github.com/stanX19/Macro_Automation.git Macro_Automation
cd Macro_Automation
py -m pip install -r requirements.txt
```

# run

```commandline
cd srcs
set PYTHONPATH=%CD%\..\srcs;%CD%\classes;%CD%\UI;%CD%\Data_manager;%CD%\utils;%CD%\hsr;%CD%\hsr\generate_templates;%PYTHONPATH%
py hsr\star_rail_main.py
```