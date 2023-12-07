import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import read_write as io
import pickle


def get_args():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description='Add cluster result to the database')

    # Define the arguments
    # Kmeans
    parser.add_argument(
        '-kmeans_k',
        type=int,
        default=5,
        help='The number of clusters in Kmeans')
    parser.add_argument(
        '-kmeans_percentile',
        type=int,
        default=95,
        help='Determine a threshold for anomaly detection based on percentile')
    # DBSCAN
    parser.add_argument(
        '-dbscan_eps',
        type=float,
        default=0.5,
        help='The eps in dbscan')
    parser.add_argument(
        '-dbscan_min_samples',
        type=int,
        default=20,
        help='The min_samples in dbscan')
    # Isolation forest
    parser.add_argument(
        '-if_contamination',
        type=float,
        default=0.05,
        help='The contamination in isolation forest, contamination is to specify the percentage of anomalies')
    # SVM
    parser.add_argument(
        '-svm_nu',
        type=float,
        default=0.05,
        help='The nu in SVM, nu is to specify the percentage of anomalies')
    # train
    parser.add_argument(
        '-train_num',
        type=int,
        default=181,
        help='Specify the train number')

    # Parse the command-line arguments
    args = parser.parse_args()
    return args


class DetectAnomaly:
    def __init__(self, args, data):
        self.args = args
        self.data = data

    def train_model(self):
        # select_data
        con_1 = (self.data["track_or_stop"] == 0)
        move = self.data[con_1]
        # random_state for reproducibility
        selected_data = move.sample(n=200000, random_state=42)
        del self.data
        # select_column_standardize
        x = selected_data[['RS_E_InAirTemp_PC1',
                           'RS_E_InAirTemp_PC2',
                           'RS_E_OilPress_PC1',
                           'RS_E_OilPress_PC2',
                           'RS_E_RPM_PC1',
                           'RS_E_RPM_PC2',
                           'RS_E_WatTemp_PC1',
                           'RS_E_WatTemp_PC2',
                           'RS_T_OilTemp_PC1',
                           'RS_T_OilTemp_PC2']]
        x = x.reset_index(drop=True)
        scaler = StandardScaler()
        scaler.fit(x)
        X = scaler.transform(x)
        self.scaler_model = scaler
        print("Scaler trained!")
        # kmeans
        kmeans = KMeans(n_clusters=self.args.kmeans_k)
        kmeans.fit(X)
        self.kmeans_model = kmeans
        print("Kmeans trained!")
        # if
        # Adjust contamination based on your dataset
        isolation_forest = IsolationForest(
            contamination=self.args.if_contamination)
        if_model = isolation_forest.fit(X)
        self.if_model = if_model
        print("Isolation forest trained!")
        # svm
        # Adjust nu based on your scenario
        svm_model = OneClassSVM(nu=self.args.svm_nu)
        svm_model.fit(X)
        self.svm_model = svm_model
        print("SVM trained!")

    def apply_model(self, data):
        self.data = data
        x = self.data[['RS_E_InAirTemp_PC1',
                       'RS_E_InAirTemp_PC2',
                       'RS_E_OilPress_PC1',
                       'RS_E_OilPress_PC2',
                       'RS_E_RPM_PC1',
                       'RS_E_RPM_PC2',
                       'RS_E_WatTemp_PC1',
                       'RS_E_WatTemp_PC2',
                       'RS_T_OilTemp_PC1',
                       'RS_T_OilTemp_PC2']]
        x = x.reset_index(drop=True)
        # apply scaler
        X = self.scaler_model.transform(x)
        # apply kmeans
        cluster_assignments = self.kmeans_model.predict(X)
        distances_to_center = pairwise_distances_argmin_min(
            X, self.kmeans_model.cluster_centers_)[1]
        threshold = np.percentile(
            distances_to_center,
            self.args.kmeans_percentile)
        anomalies_indices = np.where(distances_to_center > threshold)[0]
        kmeans_anomaly_result = - \
            (self.data.index.isin(anomalies_indices).astype(int) * 2 - 1)
        self.data['k_cluster'], self.data['k_anomaly'] = cluster_assignments, kmeans_anomaly_result
        print("Kmeans predicted!")
        # apply isolation forest
        if_labels = self.if_model.predict(X)
        self.data['if_anomaly'] = if_labels
        print("Isolation forest predicted!")
        # apply svm
        svm_labels = self.svm_model.predict(X)
        self.data["svm_anomaly"] = svm_labels
        print("SVM predicted!")
        return self.data


def main():
    # train model
    args = get_args()
    data = io.read_data(io.Filenames.data_with_weather)
    detect_anomaly = DetectAnomaly(args, data)
    detect_anomaly.train_model()
    io.write_pickle(detect_anomaly, io.Filenames.detect_anomaly)
    # apply model
    detect_anomaly_loaded = io.read_pickle(io.Filenames.detect_anomaly)
    data = io.read_data(io.Filenames.data_with_weather)
    # randomly sample some to test
    selected_data = data.sample(n=100000, random_state=1)
    anomaly_result = detect_anomaly_loaded.apply_model(selected_data)
    io.write_data(anomaly_result, io.Filenames.data_with_cluster)


if __name__ == "__main__":
    main()
