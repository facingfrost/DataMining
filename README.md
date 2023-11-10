# Data Mining Train Project

![AR41](https://upload.wikimedia.org/wikipedia/commons/c/c9/Foto_van_de_MW41_%282%29.png)
Repository for the data mining project at the ULB 2023-Fall

# Installation
The virtual environment assumes python 3.11. Create your virtual environment and activate it using:

```sh
python3.11 -m venv train_env # Creates the virtual environment
source env/bin/activate #activates the virtual environment
```
Install the dependencies used by using 

```sh
pip install -r requirements.txt
```

If you need to update the requirements, i.e. you added a new library, add it to the requirements using 
```sh
pip freeze > requirements.txt
```

To deactivate the virtual environment, open a new terminal or run the command 
```sh
deactivate
```
# Fix-Lint Autopep8
We use `autopep8` to fix the format of the code. Run the following command before pushing to the branch.
```sh
sh fix-lint.sh
```

# Data
Please add the file `data_with_weather.csv` to the data folder so that all scripts are consistent.

For reference about the meteorological data please consult this [link](https://dev.meteostat.net/formats.html#meteorological-parameters)
