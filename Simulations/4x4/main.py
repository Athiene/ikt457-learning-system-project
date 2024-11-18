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

gameboard_size = 4
Go_back = 0
csvName = f"{gameboard_size}x{gameboard_size}_goBack{Go_back}_set"

edgeList = [[] for _ in range(gameboard_size * gameboard_size)]

def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=100, type=int)
    parser.add_argument("--number-of-clauses", default=400, type=int)
    parser.add_argument("--T", default=400, type=int)
    parser.add_argument("--s", default=1.2, type=float)
    parser.add_argument("--depth", default=3, type=int)
    parser.add_argument("--hypervector-size", default=512, type=int)
    parser.add_argument("--hypervector-bits", default=2, type=int)
    parser.add_argument("--message-size", default=512, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--number-of-examples", default=50000, type=int)
    parser.add_argument('--double-hashing', dest='double_hashing', default=False, action='store_true')
    parser.add_argument("--max-included-literals", default=16, type=int)

    args = parser.parse_args()
    for key, value in kwargs.items():
        if key in args.__dict__:
            setattr(args, key, value)
    return args

def findAllEdges(board_size):
    for index in range(board_size * board_size):
        # Up-Left connection
        if index >= board_size and (index - board_size) not in edgeList[index]:
            edgeList[index].append(index - board_size)
            edgeList[index - board_size].append(index)
    
        # Up-right connection
        if index >= board_size and index % board_size != (board_size - 1) and (index - board_size + 1) not in edgeList[index]:
            edgeList[index].append(index - board_size + 1)
            edgeList[index - board_size + 1].append(index)
    
        # Down-Right connection
        if index < board_size * (board_size - 1) and (index + board_size) not in edgeList[index]:
            edgeList[index].append(index + board_size)
            edgeList[index + board_size].append(index)
    
        # Down-left connection
        if index < board_size * (board_size - 1) and index % board_size != 0 and (index + board_size - 1) not in edgeList[index]:
            edgeList[index].append(index + board_size - 1)
            edgeList[index + board_size - 1].append(index)
    
        # Right connection
        if index % board_size != (board_size - 1) and (index + 1) not in edgeList[index]:
            edgeList[index].append(index + 1)
            edgeList[index + 1].append(index)
    
        # Left connection
        if index % board_size != 0 and (index - 1) not in edgeList[index]:
            edgeList[index].append(index - 1)
            edgeList[index - 1].append(index)


def fetch_labels(labels):
    int_labels = np.array([])  # Start with an empty array
    for index in range(len(labels)):
        if labels[index][0] == 'Red':
            int_labels = np.append(int_labels, 0)
        elif labels[index][0] == 'Blue':
            int_labels = np.append(int_labels, 1)
    return int_labels


def read_from_csv(filename):
    simulations = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            winner = int(row['winner'])
            features = eval(row['feature'])
            simulations.append([winner, features])
    return simulations


args = default_args()

################## READING DATA FROM CSV #####################

findAllEdges(gameboard_size)

print("Reading data from CSV")

# Read training and testing data from CSV files
data_test = read_from_csv(csvName + "_test_data.csv")
data_training = read_from_csv(csvName + "_training_data.csv")

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
    hypervector_size=args.hypervector_size,
    hypervector_bits=args.hypervector_bits,
    double_hashing=args.double_hashing
)

for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList = simulation
    # print(simulation)
    graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_train.prepare_node_configuration()

for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList = simulation
    for node_id in range(len(edgeList)):
        if edgeList[node_id]:
            graphs_train.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

graphs_train.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList = simulation

    for node_id in range(len(edgeList)):
        # Add edges for the current node
        if edgeList[node_id]:  # Check if there are edges for the node
            for edge in edgeList[node_id]:
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
    for node_id in range(len(edgeList)):
        if edgeList[node_id]:
            graphs_test.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

graphs_test.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id, simulation in enumerate(Simulation_Test):
    winner, featureList = simulation

    for node_id in range(len(edgeList)):

        # Add edges for the current node
        if edgeList[node_id]:  # Check if there are edges for the node
            for edge in edgeList[node_id]:
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
    args.number_of_clauses,
    args.T,
    args.s,
    depth=args.depth,
    message_size=args.message_size,
    message_bits=args.message_bits,
    max_included_literals=args.max_included_literals,
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

start_training = time()
for i in range(args.epochs):
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
    print(f"Epoch#{i + 1}")
    print(f"-- Accuracy train: {accuracy_train}")
    print(f"0 VS 1 (Train): ({training_count_0}, {training_count_1})")
    print(f"-- Accuracy test: {accuracy_test}")
    print(f"0 VS 1 (Test): ({test_count_0}, {test_count_1})")
    print(f"Training Time: {training_time}")
    print(f"Testing Time: {testing_time}")
    print("")

stop_training = time()
total_time = stop_training - start_training
print(f"Total Training Time: {total_time}")

# Calculate and print averages
avg_training_time = np.mean(time_training_epochs)
avg_testing_time = np.mean(time_testing_epochs)
avg_accuracy_train = np.mean(accuracy_train_epochs)
avg_accuracy_test = np.mean(accuracy_test_epochs)

print("\nAverages:")
print(f"Average Training Time per Epoch: {avg_training_time}")
print(f"Average Testing Time per Epoch: {avg_testing_time}")
print(f"Average Training Accuracy: {avg_accuracy_train}")
print(f"Average Testing Accuracy: {avg_accuracy_test}")

hs_accuracy_test = max(accuracy_test_epochs)
hs_accuracy_train = max(accuracy_train_epochs)

print("\nBest values:")
print(f"Highest Testing Accuracy: {hs_accuracy_test}")
print(f"Highest Training Accuracy: {hs_accuracy_train}")



weights = tm.get_state()[1].reshape(2, -1)

for i in range(tm.number_of_clauses):
    print("Clause #%d W:(%d %d)" % (i, weights[0, i], weights[1, i]), end=' ')
    l = []
    for k in range(args.hypervector_size * 2):
        if tm.ta_action(0, i, k):
            if k < args.hypervector_size:
                l.append("x%d" % (k))
            else:
                l.append("NOT x%d" % (k - args.hypervector_size))
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

