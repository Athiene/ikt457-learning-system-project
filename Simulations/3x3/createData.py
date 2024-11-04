import csv
import os.path
import sys
import os 
import random
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import plotting
from HexGame import game
from GraphTsetlinMachine.graphs import Graphs
from GraphTsetlinMachine.tm import MultiClassGraphTsetlinMachine

def createCSV(board_size, examples, goBack, CSVname):
    with open(CSVname+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["winner", "feature", "edges"]
        writer.writerow(field)

        for i in range(examples):
            new_game = game.Game(board_size)
            winner, feature, edges = new_game.SimulateGame(goBack)
            writer.writerow([winner, feature, edges])


def createCSV_noSimulation(data, CSVname):
    with open(CSVname+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["winner", "feature", "edges"]
        writer.writerow(field)
        
        for i, da in enumerate(data):
            winner, feature, edges = da
            writer.writerow([winner, feature, edges])


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

def filterData(simulation_data):
    print("AMOUNT OF DATA GENERATED: ", len(simulation_data))
    
    red_wins = []
    blue_wins = []
    
    # Separate the simulation data into red and blue wins
    for simulation in simulation_data:
        winner = simulation[0]  # First element represents the winner
        if winner == "0":  # Red wins
            red_wins.append(simulation)
        elif winner == "1":  # Blue wins
            blue_wins.append(simulation)
    
    print(f"RED VS BLUE WINS: ({len(red_wins)}, {len(blue_wins)})")
    
    # Get the number of red and blue wins
    num_red_wins = len(red_wins)
    num_blue_wins = len(blue_wins)
    
    red_samples = red_wins[:num_blue_wins]
    blue_samples = blue_wins
    
    print(f"RED SAMPLES vs BLUE SAMPLES: ({len(red_samples)}, {len(blue_samples)})")
    
    red_slice = int(0.9 * len(red_samples))
    blue_slice = int(0.9 * len(blue_samples))
    
    train_red_sample = red_samples[:red_slice]
    train_blue_sample = blue_samples[:blue_slice]
    
    test_red_sample = red_samples[red_slice:]
    test_blue_sample = blue_samples[blue_slice:]
    
    # Combine red and blue wins for training and test data
    Simulation_Train = train_red_sample + train_blue_sample
    Simulation_Test = test_red_sample + test_blue_sample
    
    # Shuffle the data to ensure random placement of red and blue wins
    random.shuffle(Simulation_Train)
    random.shuffle(Simulation_Test)
    
    # Print out the amount of data used
    print("AMOUNT OF DATA USING: ", len(Simulation_Train) + len(Simulation_Test))
    
    # Convert '0' and '1' strings to integers in Y and Y_test
    Y = np.array([int(simulation[0]) for simulation in Simulation_Train])
    Y_test = np.array([int(simulation[0]) for simulation in Simulation_Test])

    print(f"Training Data vs Testing Data: ({len(Simulation_Train)},{len(Simulation_Test)}) ")
    print(
        f"Training Data - Amount RED Wins (Training vs Testing): ({len(np.where(Y == 0)[0])}, {len(np.where(Y == 1)[0])})")
    print(
        f"Testing Data - Amount BLUE Wins: (Training vs Testing): ({len(np.where(Y_test == 0)[0])}, {len(np.where(Y_test == 1)[0])})")
    return Simulation_Test, Simulation_Train

def fetch_simulation_games(number, gameboard_size, goBack, noDuplicates, randomMoves):
    red_data = []  # List to collect "Red" results
    blue_data = []  # List to collect "Blue" results
    existing_games = set()
    removed = 0

    while len(red_data) < number or len(blue_data) < number:
        new_game = game.Game(gameboard_size)
        winner, feature, edges = new_game.SimulateGame(goBack, randomMoves)

        # Create a unique key for the game based on its features and edges
        game_key = (winner, tuple(feature))

        if noDuplicates:
            if game_key in existing_games:
                removed += 1
            
            # Check if this game already exists
            if game_key not in existing_games:
                
                # Add the game to the existing set
                existing_games.add(game_key)
                
                # Check if winner is Red or Blue
                if winner == "0" and len(red_data) < number:
                    red_data.append((winner, feature, edges))  # Append red results
                elif winner == "1" and len(blue_data) < number:
                    blue_data.append((winner, feature, edges))  # Append blue results
        else:   
            # Check if winner is Red or Blue
            if winner == "0" and len(red_data) < number:
                red_data.append((winner, feature, edges))  # Append red results
            elif winner == "1" and len(blue_data) < number:
                blue_data.append((winner, feature, edges))  # Append blue results
    print(f"Duplicates: {removed}")
    return red_data + blue_data


#
# PARAMETERS
#
gameboard_size = 3
csvName = "3x3_goBack2_set"
number_of_examples = 2000
go_back=2
no_duplicates = False
random_moves = True


if os.path.isfile(csvName + "_test_data.csv") or os.path.isfile(csvName + "_training_data.csv"):
    print("Dataset with the same name already exists!")
    print("Exiting...")
    exit()

data = fetch_simulation_games(number=number_of_examples, gameboard_size=gameboard_size, goBack=go_back, noDuplicates=no_duplicates, randomMoves=random_moves)
createCSV_noSimulation(data, csvName)
test_data, training_data = filterData(simulation_data=data)
createCSV_noSimulation(test_data, csvName+"_test_data")
createCSV_noSimulation(training_data, csvName+"_training_data")
print("Created dataset!")

"""
data = createCSV(board_size=gameboard_size, examples=number_of_examples, goBack=0, csvName=csvName)
test_data, training_data = filterData(simulation_data=data)
createCSV_noSimulation(test_data, csvName+"_test_data")
createCSV_noSimulation(training_data, csvName+"_training_data")
print("Created dataset!")


import csv
from HexGame import game

def createCSV(board_size, examples, goBack, CSVname):
    with open(CSVname+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["winner", "feature", "edges"]
        writer.writerow(field)

        for i in range(examples):
            new_game = game.Game(board_size)
            winner, feature, edges = new_game.SimulateGame(goBack)
            writer.writerow([winner, feature, edges])


"""
    
    


