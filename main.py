import csv
import argparse
from GraphTsetlinMachine.graphs import Graphs
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine
import numpy as np
from time import time
import os.path
import random
from sklearn.model_selection import train_test_split


def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=100, type=int)
    parser.add_argument("--number-of-clauses", default=800, type=int)
    parser.add_argument("--T", default=400, type=int)
    parser.add_argument("--s", default=1.2, type=float)
    parser.add_argument("--depth", default=12, type=int)
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
            edges = eval(row['edges'])
            simulations.append([winner, features, edges])
    return simulations


args = default_args()
gameboard_size = 3
csvName = "3x3_set"

################## READING DATA FROM CSV #####################

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
    symbols=['R', 'B', 'N'],
    hypervector_size=args.hypervector_size,
    hypervector_bits=args.hypervector_bits,
    double_hashing=args.double_hashing
)

for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList, edgeList = simulation
    # print(simulation)
    graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_train.prepare_node_configuration()

for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList, edgeList = simulation
    for node_id in range(len(edgeList)):
        if edgeList[node_id]:
            graphs_train.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

graphs_train.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id, simulation in enumerate(Simulation_Train):
    winner, featureList, edgeList = simulation

    for node_id in range(len(edgeList)):

        # Add edges for the current node
        if edgeList[node_id]:  # Check if there are edges for the node
            for edge in edgeList[node_id]:
                graphs_train.add_graph_node_edge(graph_id, node_id, edge,
                                                 0)  # 0 could represent weight or other attribute

        # Add node properties based on features
        feature = featureList[node_id]  # Get the feature for the current node
        if feature == 'Red':
            graphs_train.add_graph_node_property(graph_id, node_id, 'R')
        elif feature == 'Blue':
            graphs_train.add_graph_node_property(graph_id, node_id, 'B')
        else:
            graphs_train.add_graph_node_property(graph_id, node_id, 'N')  # Default property

graphs_train.encode()

#### TESTING GRAPH ###

graphs_test = Graphs(
    len(Simulation_Test), init_with=graphs_train
)

for graph_id, simulation in enumerate(Simulation_Test):
    winner, featureList, edgeList = simulation
    graphs_test.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_test.prepare_node_configuration()

for graph_id, simulation in enumerate(Simulation_Test):
    winner, featureList, edgeList = simulation
    for node_id in range(len(edgeList)):
        if edgeList[node_id]:
            graphs_test.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

graphs_test.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id, simulation in enumerate(Simulation_Test):
    winner, featureList, edgeList = simulation

    for node_id in range(len(edgeList)):

        # Add edges for the current node
        if edgeList[node_id]:  # Check if there are edges for the node
            for edge in edgeList[node_id]:
                graphs_test.add_graph_node_edge(graph_id, node_id, edge,
                                                0)  # 0 could represent weight or other attribute

        # Add node properties based on features
        feature = featureList[node_id]  # Get the feature for the current node
        if feature == 'Red':
            graphs_test.add_graph_node_property(graph_id, node_id, 'R')
        elif feature == 'Blue':
            graphs_test.add_graph_node_property(graph_id, node_id, 'B')
        else:
            graphs_test.add_graph_node_property(graph_id, node_id, 'N')  # Default property

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

start_training = time()
for i in range(args.epochs):
    tm.fit(graphs_train, Y, epochs=1, incremental=True)

    train_prediction = tm.predict(graphs_train)
    test_prediction = tm.predict(graphs_test)
    print(f"Epoch#{i + 1}")
    print(f"-- Accuracy train: {np.mean(Y == train_prediction)}",
          end=' ')
    print("")
    # Count occurrences of 1s and 0s
    training_count_1 = sum(1 for prediction in train_prediction if prediction == 1)
    training_count_0 = sum(1 for prediction in train_prediction if prediction == 0)

    print(f"0 VS 1: ({training_count_0}, {training_count_1})")

    print(f"-- Accuracy test: {np.mean(Y_test == test_prediction)} ")
    # Count occurrences of 1s and 0s
    test_count_1 = sum(1 for prediction in test_prediction if prediction == 1)
    test_count_0 = sum(1 for prediction in test_prediction if prediction == 0)
    print(f"0 VS 1: ({test_count_0}, {test_count_1})")
    print("")

stop_training = time()
print(f"Time: {stop_training - start_training}")

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

