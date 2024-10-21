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
    parser.add_argument("--T", default=400, type=int)
    parser.add_argument("--s", default=0.5, type=float)
    parser.add_argument("--depth", default=3, type=int)
    parser.add_argument("--hypervector-size", default=512, type=int)
    parser.add_argument("--hypervector-bits", default=2, type=int)
    parser.add_argument("--message-size", default=512, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--number-of-examples", default=5000, type=int)
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


def prepare_graphs_training(simulations):
    for graph_id, simulation in enumerate(simulations):
        winner, featureList, edgeList = simulation
        graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

    graphs_train.prepare_node_configuration()

    for graph_id, simulation in enumerate(simulations):
        winner, featureList, edgeList = simulation
        for node_id in range(len(edgeList)):
            if edgeList[node_id]:
                graphs_train.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

    graphs_train.prepare_edge_configuration()

    # Adds actual values i.e: features and edges
    for graph_id, simulation in enumerate(simulations):
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


def prepare_graphs_testing(simulations):
    for graph_id, simulation in enumerate(simulations):
        winner, featureList, edgeList = simulation
        graphs_test.set_number_of_graph_nodes(graph_id, len(featureList))

    graphs_test.prepare_node_configuration()

    for graph_id, simulation in enumerate(simulations):
        winner, featureList, edgeList = simulation
        for node_id in range(len(edgeList)):
            if edgeList[node_id]:
                graphs_test.add_graph_node(graph_id, node_id, len(edgeList[node_id]))

    graphs_test.prepare_edge_configuration()

    # Adds actual values i.e: features and edges
    for graph_id, simulation in enumerate(simulations):
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


args = default_args()
gameboard_size = 3
csvName = "3x3_set"

if not os.path.isfile(csvName):
    createCSV(board_size=3, examples=args.number_of_examples, goBack=0, CSVname=csvName)

################## READING DATA FROM CSV #####################

print("Reading data from CSV")

# Read training and testing data from CSV files
simulation_data = read_from_csv(csvName + ".csv")

red_wins = []
blue_wins = []

#for simulation in simulation_data:
#    winner = simulation[0]  # First element represents the winner
#    if winner == 0:  # Red wins
#        Simulation_Train.append(simulation)
#   elif winner == 1:  # Blue wins
#        Simulation_Test.append(simulation)

for simulation in simulation_data:
    winner = simulation[0]  # First element represents the winner
    if winner == 0:  # Red wins
        red_wins.append(simulation)
    elif winner == 1:  # Blue wins
        blue_wins.append(simulation)

# Determine the number of samples to use for training (50% from each)
num_samples = min(len(red_wins), len(blue_wins))  # Number of samples for training

# Randomly sample half of the available Red wins and half of the available Blue wins for training
random.seed(42)  # Set a seed for reproducibility
red_train_samples = random.sample(red_wins, num_samples // 2)
blue_train_samples = random.sample(blue_wins, num_samples // 2)

# Create balanced training dataset (50% Red, 50% Blue)
Simulation_Train = red_train_samples + blue_train_samples

# Use all remaining Red win simulations for the testing dataset
Simulation_Test = [simulation for simulation in red_wins if simulation not in Simulation_Train]

# Split the data into training and testing sets
#mid_index = int(len(simulation_data) * 0.9)
#Simulation_Train = simulation_data[:mid_index]
#Simulation_Test = simulation_data[mid_index:]

Y = np.array([simulation[0] for simulation in Simulation_Train])
Y_test = np.array([simulation[0] for simulation in Simulation_Test])

print(f"Training Data vs Testing Data: ({len(Simulation_Train)},{len(Simulation_Test)}) ")
print(f"Amount RED Wins (Training vs Testing): ({len(np.where(Y == 0)[0])}, {len(np.where(Y_test == 0)[0])})")
print(f"Amount BLUE Wins: (Training vs Testing): ({len(np.where(Y == 1)[0])}, {len(np.where(Y_test == 1)[0])})")

# Initialize Graphs for training and testing
graphs_train = Graphs(len(Simulation_Train), symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                      hypervector_bits=args.hypervector_bits, double_hashing=args.double_hashing)
graphs_test = Graphs(len(Simulation_Test), symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                     hypervector_bits=args.hypervector_bits)

# Prepare the training graphs
prepare_graphs_training(Simulation_Train)
# Prepare the testing graphs
prepare_graphs_testing(Simulation_Test)

############### PREDICTION ###############

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
stop_training = time()
print(f"Time: {stop_training - start_training}")

weights = tm.get_state()[1].reshape(2, -1)
