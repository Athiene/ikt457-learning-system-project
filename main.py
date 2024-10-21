import csv
import argparse
from GraphTsetlinMachine.graphs import Graphs
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine
import numpy as np
from time import time


def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=100, type=int)
    parser.add_argument("--number-of-clauses", default=200, type=int)
    parser.add_argument("--T", default=400, type=int)
    parser.add_argument("--s", default=1.2, type=float)
    parser.add_argument("--depth", default=6, type=int)
    parser.add_argument("--hypervector-size", default=512, type=int)
    parser.add_argument("--hypervector-bits", default=2, type=int)
    parser.add_argument("--message-size", default=512, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--number-of-examples", default=1000, type=int)
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


def prepare_graphs(simulations, graphs):

    for graph_id, simulation in enumerate(simulations):
        winner, featureList, edgeList = simulation
        graphs.set_number_of_graph_nodes(graph_id, len(featureList))

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

            if edgeList[node_id]:
                for edge in edgeList[node_id]:
                    graphs.add_graph_node_edge(graph_id, node_id, edge, 0)

            if featureList[node_id] == 'Red':
                graphs.add_graph_node_property(graph_id, node_id, 'R')
            elif featureList[node_id] == 'Blue':
                graphs.add_graph_node_property(graph_id, node_id, 'B')
            else:
                graphs.add_graph_node_property(graph_id, node_id, 'N')

    graphs_train.encode()


args = default_args()
gameboard_size = 6

################## READING DATA FROM CSV #####################

print("Reading data from CSV")

# Read training and testing data from CSV files
simulation_data = read_from_csv("3x3_set.csv")

# Split the data into training and testing sets (for example, first half for training, second for testing)
mid_index = len(simulation_data) // 2
Simulation_Train = simulation_data[:mid_index]
Simulation_Test = simulation_data[mid_index:]

# Initialize Graphs for training and testing
graphs_train = Graphs(len(Simulation_Train), symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                      hypervector_bits=args.hypervector_bits, double_hashing=args.double_hashing)
graphs_test = Graphs(len(Simulation_Test), symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                     hypervector_bits=args.hypervector_bits)

# Prepare the training graphs
prepare_graphs(Simulation_Train, graphs_train)
# Prepare the testing graphs
prepare_graphs(Simulation_Test, graphs_test)

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
    tm.fit(graphs_train, fetch_labels(Simulation_Train), epochs=1, incremental=True)
    print(f"Epoch#{i + 1} -- Accuracy train: {np.mean(fetch_labels(Simulation_Train) == tm.predict(graphs_train))}",
          end=' ')
    print(f"-- Accuracy test: {np.mean(fetch_labels(Simulation_Test) == tm.predict(graphs_test))} ")
stop_training = time()
print(f"Time: {stop_training - start_training}")

weights = tm.get_state()[1].reshape(2, -1)
