import csv
import argparse
from GraphTsetlinMachine.graphs import Graphs
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine
import numpy as np
from time import time
from createData import createCSV
import os.path
import random


def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=100, type=int)
    parser.add_argument("--number-of-clauses", default=200, type=int)
    parser.add_argument("--T", default=4000, type=int)
    parser.add_argument("--s", default=1, type=float)
    parser.add_argument("--depth", default=6, type=int)
    parser.add_argument("--hypervector-size", default=512, type=int)
    parser.add_argument("--hypervector-bits", default=2, type=int)
    parser.add_argument("--message-size", default=512, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--number-of-examples", default=6000, type=int)
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

if os.path.isfile(csvName + ".csv"):
    print("FILE ALREADY EXISTS")

# createCSV(board_size=3, examples=args.number_of_examples, goBack=0, CSVname=csvName)

################## READING DATA FROM CSV #####################

print("Reading data from CSV")

# Read training and testing data from CSV files
simulation_data = read_from_csv(csvName + ".csv")

print("AMOUNT OF DATA GENERATED: ", len(simulation_data))

red_wins = []
blue_wins = []

# Separate the simulation data into red and blue wins
for simulation in simulation_data:
    winner = simulation[0]  # First element represents the winner
    if winner == 0:  # Red wins
        red_wins.append(simulation)
    elif winner == 1:  # Blue wins
        blue_wins.append(simulation)

print(f"RED VS BLUE WINS: ({len(red_wins)}, {len(blue_wins)})")

# Get the number of red and blue wins
num_red_wins = len(red_wins)
num_blue_wins = len(blue_wins)

# Ensure the number of red and blue wins is even for both training and testing
max_even_wins = num_blue_wins

# Split data for training (90%) and testing (10%)
num_train_samples = int(max_even_wins * 0.9)  # 90% for training
num_test_samples = max_even_wins - num_train_samples  # 10% for testing

# Determine number of red and blue wins for training and testing
red_train_samples_count = num_train_samples // 2
blue_train_samples_count = num_train_samples // 2
red_test_samples_count = num_test_samples // 2
blue_test_samples_count = num_test_samples // 2

# Randomly sample for training data
random.seed(42)  # Set a seed for reproducibility
red_train_samples = random.sample(red_wins, red_train_samples_count)
blue_train_samples = random.sample(blue_wins, blue_train_samples_count)

# Ensure enough samples remain for testing
remaining_red_wins = [x for x in red_wins if x not in red_train_samples]
remaining_blue_wins = [x for x in blue_wins if x not in blue_train_samples]

# Adjust the test sample counts based on remaining samples
red_test_samples_count = min(red_test_samples_count, len(remaining_red_wins))
blue_test_samples_count = min(blue_test_samples_count, len(remaining_blue_wins))

# Determine the maximum number of test samples we can take to ensure equality
max_test_samples = min(len(remaining_red_wins), len(remaining_blue_wins), red_test_samples_count,
                       blue_test_samples_count)

# Adjust the counts for testing samples
red_test_samples_count = max_test_samples
blue_test_samples_count = max_test_samples

# Randomly sample test data
red_test_samples = random.sample(remaining_red_wins, red_test_samples_count)
blue_test_samples = random.sample(remaining_blue_wins, blue_test_samples_count)

# Combine red and blue wins for training and test data
Simulation_Train = red_train_samples + blue_train_samples
Simulation_Test = red_test_samples + blue_test_samples

# Shuffle the data to ensure random placement of red and blue wins
random.shuffle(Simulation_Train)
random.shuffle(Simulation_Test)

# Print out the amount of data used
print("AMOUNT OF DATA USING: ", len(Simulation_Train) + len(Simulation_Test))

Y = np.array([simulation[0] for simulation in Simulation_Train])
Y_test = np.array([simulation[0] for simulation in Simulation_Test])

for i in range(len(Simulation_Test)):
    print(Simulation_Test[i])

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
    # double_hashing=args.double_hashing
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
)

start_training = time()
for i in range(args.epochs):
    tm.fit(graphs_train, Y, epochs=1, incremental=True)
    print(f"Epoch#{i + 1} -- Accuracy train: {np.mean(Y == tm.predict(graphs_train))}",
          end=' ')
    print(f"-- Accuracy test: {np.mean(Y_test == tm.predict(graphs_test))} ")
    # Assuming tm is your model and graphs_train is your input data
    predictions = tm.predict(graphs_train)
    # Count occurrences of 1s and 0s
    count_1 = sum(1 for prediction in predictions if prediction == 1)
    count_0 = sum(1 for prediction in predictions if prediction == 0)
    # Print the counts
    print(f"0 VS 1: ({count_0}, {count_1})")
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

