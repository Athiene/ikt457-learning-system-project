import csv
import argparse
import sys
import os 
import numpy as np
from time import time
import random
from sklearn.model_selection import train_test_split
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import plotting
from GraphTsetlinMachine.graphs import Graphs
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine


class Main:
    def __init__(self, Args, gameboard_size, Go_back, csvName):

        self.csvName = f"{gameboard_size}x{gameboard_size}_goBack{Go_back}_set"
        self.args = Args
        self.edgeList = [[] for _ in range(gameboard_size * gameboard_size)]

        ################## READING DATA FROM CSV #####################
    
        self.findAllEdges(gameboard_size)
        
        print("Reading data from CSV")
        
        # Read training and testing data from CSV files
        data_test = self.read_from_csv(csvName + "_test_data.csv")
        data_training = self.read_from_csv(csvName + "_training_data.csv")
        
        # Combine red and blue wins for training and test data
        Simulation_Test = data_test
        Simulation_Train = data_training
        
        # Print out the amount of data used
        print("AMOUNT OF DATA USING: ", len(Simulation_Train) + len(Simulation_Test))
        
        Y = np.array([simulation[0] for simulation in Simulation_Train])
        Y_test = np.array([simulation[0] for simulation in Simulation_Test])
        
        
        print("Y: ", Y)
        print("Y_test: ", Y_test)
        
        print(f"Training Data vs Testing Data: ({len(Simulation_Train)},{len(Simulation_Test)}) ")
        print(
            f"Training Data - Amount RED Wins (Training vs Testing): ({len(np.where(Y == 0)[0])}, {len(np.where(Y == 1)[0])})")
        print(
            f"Testing Data - Amount BLUE Wins: (Training vs Testing): ({len(np.where(Y_test == 0)[0])}, {len(np.where(Y_test == 1)[0])})")
        
        ### TRAINING GRAPH ###
        
        graphs_train = Graphs(
            len(Simulation_Train),
            symbols=['X', 'O', '*'],
            hypervector_size=self.args.hypervector_size,
            hypervector_bits=self.args.hypervector_bits,
            double_hashing=self.args.double_hashing
        )
        
        for graph_id, simulation in enumerate(Simulation_Train):
            winner, featureList = simulation
            # print(simulation)
            graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))
        
        graphs_train.prepare_node_configuration()
        
        for graph_id, simulation in enumerate(Simulation_Train):
            winner, featureList = simulation
            for node_id in range(len(self.edgeList)):
                if self.edgeList[node_id]:
                    graphs_train.add_graph_node(graph_id, node_id, len(self.edgeList[node_id]))
        
        graphs_train.prepare_edge_configuration()
        
        # Adds actual values i.e: features and edges
        for graph_id, simulation in enumerate(Simulation_Train):
            winner, featureList = simulation
        
            for node_id in range(len(self.edgeList)):
                # Add edges for the current node
                if self.edgeList[node_id]:  # Check if there are edges for the node
                    for edge in self.edgeList[node_id]:
                        if featureList[node_id] == featureList[edge]:
                            #print(f"## CONNECTED ## SOURCE: {featureList[node_id]} -> DESTINATION: {featureList[edge]}")
                            graphs_train.add_graph_node_edge(graph_id=graph_id, source_node_name=node_id, destination_node_name=edge, edge_type_name="Connected")
                        else:
                            graphs_train.add_graph_node_edge(graph_id=graph_id, source_node_name=node_id, destination_node_name=edge, edge_type_name="Not Connected")
                            #print(f"## NOT CONNECTED ## SOURCE: {featureList[node_id]} -> DESTINATION: {featureList[edge]}")
        
                # Add node properties based on features
                feature = featureList[node_id]  # Get the feature for the current node
                if feature == 'Red':
                    graphs_train.add_graph_node_property(graph_id, node_id, 'X')
                elif feature == 'Blue':
                    graphs_train.add_graph_node_property(graph_id, node_id, 'O')
                else:
                    graphs_train.add_graph_node_property(graph_id, node_id, '*')  
        
        graphs_train.encode()
        
        #### TESTING GRAPH ###
        
        graphs_test = Graphs(
            len(Simulation_Test), init_with=graphs_train
        )
        
        for graph_id, simulation in enumerate(Simulation_Test):
            winner, featureList = simulation
            graphs_test.set_number_of_graph_nodes(graph_id, len(featureList))
        
        graphs_test.prepare_node_configuration()
        
        for graph_id, simulation in enumerate(Simulation_Test):
            winner, featureList = simulation
            for node_id in range(len(self.edgeList)):
                if self.edgeList[node_id]:
                    graphs_test.add_graph_node(graph_id, node_id, len(self.edgeList[node_id]))
        
        graphs_test.prepare_edge_configuration()
        
        # Adds actual values i.e: features and edges
        for graph_id, simulation in enumerate(Simulation_Test):
            winner, featureList = simulation
        
            for node_id in range(len(self.edgeList)):
        
                # Add edges for the current node
                if self.edgeList[node_id]:  # Check if there are edges for the node
                    for edge in self.edgeList[node_id]:
                        if featureList[node_id] == featureList[edge]:
                            #print(f"## Connected ## SOURCE: {featureList[node_id]} -> DESTINATION: {featureList[edge]}")
                            graphs_test.add_graph_node_edge(graph_id=graph_id, source_node_name=node_id, destination_node_name=edge, edge_type_name="Connected")
                        else:
                            #print(f"## NOT CONNECTED ## SOURCE: {featureList[node_id]} -> DESTINATION: {featureList[edge]}")
                            graphs_test.add_graph_node_edge(graph_id=graph_id, source_node_name=node_id, destination_node_name=edge, edge_type_name="Not Connected")
        
                # Add node properties based on features
                feature = featureList[node_id]  # Get the feature for the current node
                if feature == 'Red':
                    graphs_test.add_graph_node_property(graph_id, node_id, 'X')
                elif feature == 'Blue':
                    graphs_test.add_graph_node_property(graph_id, node_id, 'O')
                else:
                    graphs_test.add_graph_node_property(graph_id, node_id, '*')  # Default property
        
        graphs_test.encode()
        
        ### PREDICTION ####
        
        # Train the Tsetlin Machine
        tm = MultiClassGraphTsetlinMachine(
            self.args.number_of_clauses,
            self.args.T,
            self.args.s,
            depth=self.args.depth,
            message_size=self.args.message_size,
            message_bits=self.args.message_bits,
            max_included_literals=self.args.max_included_literals,
            grid=(16 * 13, 1, 1),
            block=(128, 1, 1)
        )
        
        # Lists to store the times and accuracies
        time_training_epochs = []
        time_testing_epochs = []
        accuracy_train_epochs = []
        accuracy_test_epochs = []
        prediction_distribution_train = []
        prediction_distribution_test = []

        with open(csvName+"epoch_log.txt", 'w') as epoch_log_file:
            start_training = time()
            for i in range(self.args.epochs):
                start_training_epoch = time()
                
                # Train the model for one epoch
                tm.fit(graphs_train, Y, epochs=1, incremental=True)
                
                # Record the training time
                stop_training_epoch = time()
                training_time = stop_training_epoch - start_training_epoch
                time_training_epochs.append(training_time)
                
                # Get training predictions
                train_prediction = tm.predict(graphs_train)
                
                # Calculate training accuracy
                accuracy_train = np.mean(Y == train_prediction)
                accuracy_train_epochs.append(accuracy_train)
                
                # Count occurrences of 1s and 0s in training predictions
                training_count_1 = sum(1 for prediction in train_prediction if prediction == 1)
                training_count_0 = sum(1 for prediction in train_prediction if prediction == 0)
                prediction_distribution_train.append((training_count_0, training_count_1))
            
                # Record the testing time
                start_testing_epoch = time()
                
                # Get testing predictions
                test_prediction = tm.predict(graphs_test)
                
                stop_testing_epoch = time()
                testing_time = stop_testing_epoch - start_testing_epoch
                time_testing_epochs.append(testing_time)
                
                # Calculate testing accuracy
                accuracy_test = np.mean(Y_test == test_prediction)
                accuracy_test_epochs.append(accuracy_test)
                
                # Count occurrences of 1s and 0s in testing predictions
                test_count_1 = sum(1 for prediction in test_prediction if prediction == 1)
                test_count_0 = sum(1 for prediction in test_prediction if prediction == 0)
                prediction_distribution_test.append((test_count_0, test_count_1))
            
                # Print epoch details
                epoch_log_file.write(f"Epoch#{i + 1}")
                epoch_log_file.write(f"-- Accuracy train: {accuracy_train}")
                epoch_log_file.write(f"0 VS 1 (Train): ({training_count_0}, {training_count_1})")
                epoch_log_file.write(f"-- Accuracy test: {accuracy_test}")
                epoch_log_file.write(f"0 VS 1 (Test): ({test_count_0}, {test_count_1})")
                epoch_log_file.write(f"Training Time: {training_time}")
                epoch_log_file.write(f"Testing Time: {testing_time}")
                epoch_log_file.write("")
        
        stop_training = time()
        total_time = stop_training - start_training
        with open(csvName+"summary_log.txt", 'w') as summary_log_file:
            print(f"Total Training Time: {total_time}")
            
            # Calculate and print averages
            avg_training_time = np.mean(time_training_epochs)
            avg_testing_time = np.mean(time_testing_epochs)
            avg_accuracy_train = np.mean(accuracy_train_epochs)
            avg_accuracy_test = np.mean(accuracy_test_epochs)
            
            summary_log_file.write("\nAverages:")
            summary_log_file.write(f"Average Training Time per Epoch: {avg_training_time}")
            summary_log_file.write(f"Average Testing Time per Epoch: {avg_testing_time}")
            summary_log_file.write(f"Average Training Accuracy: {avg_accuracy_train}")
            summary_log_file.write(f"Average Testing Accuracy: {avg_accuracy_test}")
            
            hs_accuracy_test = max(accuracy_test_epochs)
            hs_accuracy_train = max(accuracy_train_epochs)
            
            summary_log_file.write("\nBest values:")
            summary_log_file.write(f"Highest Testing Accuracy: {hs_accuracy_test}")
            summary_log_file.write(f"Highest Training Accuracy: {hs_accuracy_train}")
        
        with open(csvName+"parameters_log.txt", "w") as parameters_log_file:
            parameters_log_file.write(Args)
        
        weights = tm.get_state()[1].reshape(2, -1)
        
        for i in range(tm.number_of_clauses):
            print("Clause #%d W:(%d %d)" % (i, weights[0, i], weights[1, i]), end=' ')
            l = []
            for k in range(self.rgs.hypervector_size * 2):
                if tm.ta_action(0, i, k):
                    if k < self.args.hypervector_size:
                        l.append("x%d" % (k))
                    else:
                        l.append("NOT x%d" % (k - self.args.hypervector_size))
            print(" AND ".join(l))
            print(f"Number of literals: {len(l)}")
        
        plotting.double_plot(values_1=accuracy_train_epochs, 
                            values_2=accuracy_test_epochs, 
                            x_label="Epoch", y_label="%", 
                            title_name="Training & Test Accuracy", 
                            file_name=csvName+"AccuractValues", 
                            labels=["Train", "Test"], 
                            kvalue1=avg_accuracy_train, 
                            kvalue2=avg_accuracy_test
                            )
        
        plotting.double_plot(values_1=time_training_epochs, 
                            values_2=time_testing_epochs, 
                            x_label="Epoch", y_label="sec", 
                            title_name="Training & Test Time", 
                            file_name=csvName+"TimeValues", 
                            labels=["Train", "Test"], 
                            kvalue1=avg_training_time, 
                            kvalue2=avg_testing_time
                            )
        
        plotting.plot_moves_distribution(simulation_train=Simulation_Train, 
                                        simulation_test=Simulation_Test, 
                                        title_name="Move Distribution", 
                                        x_label="Moves", y_label="Frequency", 
                                        file_name=csvName+"MoveDistribution"
                                        )
        
    def findAllEdges(self, board_size):
        for index in range(board_size * board_size):
            # Up-Left connection
            if index >= board_size and (index - board_size) not in self.edgeList[index]:
                self.edgeList[index].append(index - board_size)
                self.edgeList[index - board_size].append(index)
        
            # Up-right connection
            if index >= board_size and index % board_size != (board_size - 1) and (index - board_size + 1) not in self.edgeList[index]:
                self.edgeList[index].append(index - board_size + 1)
                self.edgeList[index - board_size + 1].append(index)
        
            # Down-Right connection
            if index < board_size * (board_size - 1) and (index + board_size) not in self.edgeList[index]:
                self.edgeList[index].append(index + board_size)
                self.edgeList[index + board_size].append(index)
        
            # Down-left connection
            if index < board_size * (board_size - 1) and index % board_size != 0 and (index + board_size - 1) not in self.edgeList[index]:
                self.edgeList[index].append(index + board_size - 1)
                self.edgeList[index + board_size - 1].append(index)
        
            # Right connection
            if index % board_size != (board_size - 1) and (index + 1) not in self.edgeList[index]:
                self.edgeList[index].append(index + 1)
                self.edgeList[index + 1].append(index)
        
            # Left connection
            if index % board_size != 0 and (index - 1) not in self.edgeList[index]:
                self.edgeList[index].append(index - 1)
                self.edgeList[index - 1].append(index)
    
    
    def fetch_labels(self, labels):
        int_labels = np.array([])  # Start with an empty array
        for index in range(len(labels)):
            if labels[index][0] == 'Red':
                int_labels = np.append(int_labels, 0)
            elif labels[index][0] == 'Blue':
                int_labels = np.append(int_labels, 1)
        return int_labels
    
    
    def read_from_csv(self, filename):
        simulations = []
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                winner = int(row['winner'])
                features = eval(row['feature'])
                simulations.append([winner, features])
        return simulations
    
    def log_training_test(self, ):
        return
    


