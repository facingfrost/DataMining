# Data Mining Train Project

![AR41](https://upload.wikimedia.org/wikipedia/commons/c/c9/Foto_van_de_MW41_%282%29.png)
Repository for the data mining project at the ULB 2023-Fall

# Installation
The virtual environment assumes python 3.11. Create your virtual environment and activate it using:

```sh
# Creates the virtual environment
python3.11 -m venv train_env 
#activates the virtual environment
source train_env/bin/activate 
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
Please add the file `ar41_for_ulb.csv` to the data folder so that all scripts are consistent.

## Order of running the scripts
Please run in order 
```sh
python src/scripts/make_parquet_from_csv.py
python src/scripts/clean_location.py
python src/scripts/clean_outliers.py
python src/scripts/mark_stop_track.py 
python src/scripts/add_weather.py
```

For reference about the meteorological data please consult this [link](https://dev.meteostat.net/formats.html#meteorological-parameters)

# Cluster
Run the script and config the parameters:
```sh
python src/scripts/get_cluster_result.py -kmeans_k 5 -kmeans_percentile 95 -dbscan_eps 0.5 -dbscan_min_samples 20 -if_contamination 0.05 -svm_nu 0.05 -train_num 181
```
Added columns explanation:

k_cluster: The cluster the point belongs to(0,1,2,3...) calculated by kmeans

k_anomaly: Whether it's an anomaly, detected by threshold(-1,1)

db_cluster: The cluster the point belongs to(-1,0,1,2...) calculated by dbscan

if_cluster: The cluster the point belongs to(-1,1) calculated by isolation forest

svm_cluster: The cluster the point belongs to(-1,1) calculated by svm one class

# Pickle for models
Run the script and config the parameters:
```sh
python src/scripts/dump_load_pickle.py -kmeans_k 5 -kmeans_percentile 95 -dbscan_eps 0.5 -dbscan_min_samples 20 -if_contamination 0.05 -svm_nu 0.05 -train_num 181
```

# Dashboard

For the dashboard please set up docker first using 
```
docker compose up -d
```

Afterwards upload the data to questdb using 
```
python src/scripts/upload_data_to_timescaledb.py 
```
It should take around one minute to upload. 

Now you can go to `localhost:3000` and a dashboard should appear.
The user is `gabriel` and the password is `gabriel`

To reset grafana and delete cached items you can use 
```
rm dashboard/grafana/lib/grafana.db
```