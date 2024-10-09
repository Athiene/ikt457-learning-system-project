from GraphTsetlinMachine.graphs import Graphs
import argparse
from HexGame import game


def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=25, type=int)
    parser.add_argument("--number-of-clauses", default=20, type=int)
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
    parser.add_argument("--max-included-literals", default=2, type=int)

    args = parser.parse_args()
    for key, value in kwargs.items():
        if key in args.__dict__:
            setattr(args, key, value)
    return args

args = default_args()

# Lists that contain all the simulated hex games
Simulation = [[[],[],[]] for _ in range(args.number_of_examples)]

graphs_train = Graphs(args.number_of_examples, symbol_names=['R', 'B', 'N'], hypervector_size=args.hypervector_size, hypervector_bits=args.hypervector_bits)
for graph_id in range(args.number_of_examples):
    # Fetches simulated game of hex
    newGame_ = game.Game(6)
    winner, featureList, edgeList = newGame_.SimulateGame(1)
    Simulation[graph_id][0] = winner
    Simulation[graph_id][1] = featureList
    Simulation[graph_id][2] = edgeList
    # Sets the correct amount of nodes in a graph
    graphs_train.set_number_of_graph_nodes(graph_id, len(featureList))

graphs_train.prepare_node_configuration()

for graph_id in range(args.number_of_examples):
    # Sets the correct amount of edges for each node for each graph_id in the tsetlin machine node config
    for node_id in range(len(Simulation[graph_id][2])):
        graphs_train.add_graph_node(graph_id, node_id, len(Simulation[graph_id][2][node_id]))

graphs_train.prepare_edge_configuration()

print(Simulation[0][0][0])
print("###########")
for i in range(len(Simulation[0][1])):
    print(Simulation[0][1][i])
print("###########")
for i in range(len(Simulation[0][2])):
    print(Simulation[0][2][i])


# Adds actual values i.e: features and edges
for graph_id in range(args.number_of_examples):
    for node_id in range(len(Simulation[graph_id][2])):
        if Simulation[graph_id][2][node_id]:
            for edge in Simulation[graph_id][2][node_id]:
                graphs_train.add_graph_node_edge(graph_id, node_id, edge, 0)

    for node_id in range(len(Simulation[graph_id][2])):
        if Simulation[graph_id][1][node_id] == 'Red':
            graphs_train.add_graph_node_feature(graph_id, node_id, 'R')
            continue
        if Simulation[graph_id][1][node_id] == 'Blue':
            graphs_train.add_graph_node_feature(graph_id, node_id, 'B')
            continue
        if Simulation[graph_id][1][node_id] == [None]:
            graphs_train.add_graph_node_feature(graph_id, node_id, 'N')

graphs_train.encode()
