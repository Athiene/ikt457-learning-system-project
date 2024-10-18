from GraphTsetlinMachine.graphs import Graphs
from scipy.sparse import csr_matrix
import argparse
from HexGame import game
from time import time
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine
import numpy as np


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
    # print(int_labels)
    return int_labels


def print_gameboards(simulations, gameboard_size):
    for game_index, simulation in enumerate(simulations):
        print(f"Game {game_index + 1}:")

        # Create a new game object with the same board size
        newGame_ = game.Game(gameboard_size)

        # Populate the game object with the simulated features and edges
        newGame_.CellNodesFeatureList = simulation[1]  # Load the feature list
        newGame_.CellNodesEdgeList = simulation[2]  # Load the edge list

        # Print the current game state
        newGame_.print_hex_diagram()


args = default_args()
gameboard_size = 6

################## CREATING TRAINING DATA #####################

print("Creating training data")

# Lists that contain all the simulated hex games
Simulation_Train = [[[], [], [], []] for _ in range(args.number_of_examples)]

graphs_train = Graphs(args.number_of_examples, symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                      hypervector_bits=args.hypervector_bits, double_hashing=args.double_hashing, )
for graph_id in range(args.number_of_examples):
    # Fetches simulated game of hex
    newGame_ = game.Game(gameboard_size)
    winner, featureList, edgeList, maxEdges = newGame_.SimulateGame(goBack=0)
    Simulation_Train[graph_id][0] = winner
    Simulation_Train[graph_id][1] = featureList
    Simulation_Train[graph_id][2] = edgeList
    Simulation_Train[graph_id][3] = maxEdges
    # Sets the correct amount of nodes in a graph
    graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_train.prepare_node_configuration()

for graph_id in range(args.number_of_examples):
    # Sets the correct amount of edges for each node for each graph_id in the tsetlin machine node config
    for node_id in range(len(Simulation_Train[graph_id][3])):
        graphs_train.add_graph_node(graph_id, node_id, Simulation_Train[graph_id][3][node_id])

graphs_train.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id in range(args.number_of_examples):
    for node_id in range(len(Simulation_Train[graph_id][2])):
        if Simulation_Train[graph_id][2][node_id]:
            for edge in Simulation_Train[graph_id][2][node_id]:
                graphs_train.add_graph_node_edge(graph_id, node_id, edge, 0)

    for node_id in range(len(Simulation_Train[graph_id][2])):
        if Simulation_Train[graph_id][1][node_id] == 'Red':
            graphs_train.add_graph_node_property(graph_id, node_id, 'R')
            continue
        if Simulation_Train[graph_id][1][node_id] == 'Blue':
            graphs_train.add_graph_node_property(graph_id, node_id, 'B')
            continue
        if Simulation_Train[graph_id][1][node_id] == [None]:
            graphs_train.add_graph_node_property(graph_id, node_id, 'N')

graphs_train.encode()

######### CREATING TESTING DATA #####################

print("Creating testing data")

Simulation_Test = [[[], [], [], []] for _ in range(args.number_of_examples)]

graphs_test = Graphs(args.number_of_examples, symbols=['R', 'B', 'N'], hypervector_size=args.hypervector_size,
                     hypervector_bits=args.hypervector_bits)
for graph_id in range(args.number_of_examples):
    # Fetches simulated game of hex
    newGame_ = game.Game(gameboard_size)
    winner, featureList, edgeList, maxEdges = newGame_.SimulateGame(goBack=0)
    Simulation_Test[graph_id][0] = winner
    Simulation_Test[graph_id][1] = featureList
    Simulation_Test[graph_id][2] = edgeList
    Simulation_Test[graph_id][3] = maxEdges
    # Sets the correct amount of nodes in a graph
    graphs_test.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_test.prepare_node_configuration()

for graph_id in range(args.number_of_examples):
    # Sets the correct amount of edges for each node for each graph_id in the tsetlin machine node config
    for node_id in range(len(Simulation_Test[graph_id][3])):
        graphs_test.add_graph_node(graph_id, node_id, Simulation_Test[graph_id][3][node_id])

graphs_test.prepare_edge_configuration()

# Adds actual values i.e: features and edges
for graph_id in range(args.number_of_examples):
    for node_id in range(len(Simulation_Test[graph_id][2])):
        if Simulation_Test[graph_id][2][node_id]:
            for edge in Simulation_Test[graph_id][2][node_id]:
                graphs_test.add_graph_node_edge(graph_id, node_id, edge, 0)

    for node_id in range(len(Simulation_Test[graph_id][2])):
        if Simulation_Test[graph_id][1][node_id] == 'Red':
            graphs_test.add_graph_node_property(graph_id, node_id, 'R')
            continue
        if Simulation_Test[graph_id][1][node_id] == 'Blue':
            graphs_test.add_graph_node_property(graph_id, node_id, 'B')
            continue
        if Simulation_Test[graph_id][1][node_id] == [None]:
            graphs_test.add_graph_node_property(graph_id, node_id, 'N')

graphs_test.encode()

############### PREDUICTION ###############

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
