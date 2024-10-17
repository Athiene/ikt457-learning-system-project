from GraphTsetlinMachine.graphs import Graphs
from scipy.sparse import csr_matrix
import argparse
from HexGame import game
from time import time
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine
import numpy as np


def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=25, type=int)
    parser.add_argument("--number-of-clauses", default=10000, type=int)
    parser.add_argument("--T", default=200, type=int)
    parser.add_argument("--s", default=1.0, type=float)
    parser.add_argument("--depth", default=1, type=int)
    parser.add_argument("--hypervector-size", default=16, type=int)
    parser.add_argument("--hypervector-bits", default=1, type=int)
    parser.add_argument("--message-size", default=256, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--noise", default=0.2, type=float)
    parser.add_argument("--number-of-examples", default=10000, type=int)
    parser.add_argument("--max-sequence-length", default=1000, type=int)
    parser.add_argument("--number-of-classes", default=2, type=int)
    parser.add_argument("--max-included-literals", default=3, type=int)

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
    print(int_labels)
    return int_labels

args = default_args()
gameboard_size = 6

# Lists that contain all the simulated hex games
Simulation_Train = [[[],[],[]] for _ in range(args.number_of_examples)]

print("Creating training data")

graphs_train = Graphs(args.number_of_examples, symbol_names=['R', 'B', 'N'], hypervector_size=args.hypervector_size, hypervector_bits=args.hypervector_bits)
for graph_id in range(args.number_of_examples):
    # Fetches simulated game of hex
    newGame_ = game.Game(gameboard_size)
    winner, featureList, edgeList = newGame_.SimulateGame(0)
    Simulation_Train[graph_id][0] = winner
    Simulation_Train[graph_id][1] = featureList
    Simulation_Train[graph_id][2] = edgeList
    # Sets the correct amount of nodes in a graph
    graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_train.prepare_node_configuration()

for graph_id in range(args.number_of_examples):
    # Sets the correct amount of edges for each node for each graph_id in the tsetlin machine node config
    for node_id in range(len(Simulation_Train[graph_id][2])):
        graphs_train.add_graph_node(graph_id, node_id, len(Simulation_Train[graph_id][2][node_id]))

graphs_train.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id in range(args.number_of_examples):
    for node_id in range(len(Simulation_Train[graph_id][2])):
        if Simulation_Train[graph_id][2][node_id]:
            for edge in Simulation_Train[graph_id][2][node_id]:
                graphs_train.add_graph_node_edge(graph_id, node_id, edge, 0)

    for node_id in range(len(Simulation_Train[graph_id][2])):
        if Simulation_Train[graph_id][1][node_id] == 'Red':
            graphs_train.add_graph_node_feature(graph_id, node_id, 'R')
            continue
        if Simulation_Train[graph_id][1][node_id] == 'Blue':
            graphs_train.add_graph_node_feature(graph_id, node_id, 'B')
            continue
        if Simulation_Train[graph_id][1][node_id] == [None]:
            graphs_train.add_graph_node_feature(graph_id, node_id, 'N')

graphs_train.encode()

print("Creating testing data")

Simulation_Test = [[[],[],[]] for _ in range(args.number_of_examples)]

graphs_test = Graphs(args.number_of_examples, symbol_names=['R', 'B', 'N'], hypervector_size=args.hypervector_size, hypervector_bits=args.hypervector_bits)
for graph_id in range(args.number_of_examples):
    # Fetches simulated game of hex
    newGame_ = game.Game(gameboard_size)
    winner, featureList, edgeList = newGame_.SimulateGame(0)
    Simulation_Test[graph_id][0] = winner
    Simulation_Test[graph_id][1] = featureList
    Simulation_Test[graph_id][2] = edgeList
    # Sets the correct amount of nodes in a graph
    graphs_test.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_test.prepare_node_configuration()

for graph_id in range(args.number_of_examples):
    # Sets the correct amount of edges for each node for each graph_id in the tsetlin machine node config
    for node_id in range(len(Simulation_Test[graph_id][2])):
        graphs_test.add_graph_node(graph_id, node_id, len(Simulation_Test[graph_id][2][node_id]))

graphs_test.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id in range(args.number_of_examples):
    for node_id in range(len(Simulation_Test[graph_id][2])):
        if Simulation_Test[graph_id][2][node_id]:
            for edge in Simulation_Test[graph_id][2][node_id]:
                graphs_test.add_graph_node_edge(graph_id, node_id, edge, 0)

    for node_id in range(len(Simulation_Test[graph_id][2])):
        if Simulation_Test[graph_id][1][node_id] == 'Red':
            graphs_test.add_graph_node_feature(graph_id, node_id, 'R')
            continue
        if Simulation_Test[graph_id][1][node_id] == 'Blue':
            graphs_test.add_graph_node_feature(graph_id, node_id, 'B')
            continue
        if Simulation_Test[graph_id][1][node_id] == [None]:
            graphs_test.add_graph_node_feature(graph_id, node_id, 'N')

graphs_test.encode()

tm = MultiClassGraphTsetlinMachine(args.number_of_clauses, args.T, args.s, depth=args.depth, message_size = args.message_size, message_bits = args.message_bits, max_included_literals=args.max_included_literals)

for i in range(args.epochs):
    start_training = time()
    tm.fit(graphs_train, fetch_labels(Simulation_Train), epochs=1, incremental=True)
    stop_training = time()

    start_testing = time()
    result_test = 100*(tm.predict(graphs_test) == fetch_labels(Simulation_Test)).mean()
    stop_testing = time()

    result_train = 100*(tm.predict(graphs_train) == fetch_labels(Simulation_Train)).mean()

    print("%d %.2f %.2f %.2f %.2f" % (i, result_train, result_test, stop_training-start_training, stop_testing-start_testing))

weights = tm.get_state()[1].reshape(2, -1)

"""
for i in range(tm.number_of_clauses):
        print("Clause #%d W:(%d %d)" % (i, weights[0,i], weights[1,i]), end=' ')
        l = []
        for k in range(args.hypervector_size * 2):
            if tm.ta_action(0, i, k):
                if k < args.hypervector_size:
                    l.append("x%d" % (k))
                else:
                    l.append("NOT x%d" % (k - args.hypervector_size))
        print(" AND ".join(l))
"""
