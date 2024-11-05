import csv
import os.path
import sys
import os 
import random
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import plotting
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
    
    # Balance the number of red and blue wins
    num_red_wins = len(red_wins)
    num_blue_wins = len(blue_wins)
    red_samples = red_wins[:num_blue_wins]
    blue_samples = blue_wins
    
    print(f"RED SAMPLES vs BLUE SAMPLES: ({len(red_samples)}, {len(blue_samples)})")
    
    red_slice = int(0.9 * len(red_samples))
    blue_slice = int(0.9 * len(blue_samples))
    
    # Split into initial training and test sets
    train_red_sample = red_samples[:red_slice]
    train_blue_sample = blue_samples[:blue_slice]
    test_red_sample = red_samples[red_slice:]
    test_blue_sample = blue_samples[blue_slice:]
    
    # Combine red and blue wins for training and test data
    Simulation_Train = train_red_sample + train_blue_sample
    
    # Ensure no duplicates from training set in the test set
    training_set_keys = set((sim[0], tuple(sim[1])) for sim in Simulation_Train)
    Simulation_Test = [
        sim for sim in (test_red_sample + test_blue_sample)
        if (sim[0], tuple(sim[1])) not in training_set_keys
    ]
    
    # Calculate the target test set size (10% of total data)
    desired_test_size = int(0.1 * len(simulation_data))

    print(f"Unique Test data: {len(Simulation_Test)}")
    print(f"Required duplications : {desired_test_size-len(Simulation_Test)}")
    
    duplicated_count = 0
    # If test set is too small, duplicate random samples within the test set until it reaches the target size
    while len(Simulation_Test) < desired_test_size:
        duplicate_sample = random.choice(Simulation_Test)
        duplicated_count += 1
        Simulation_Test.append(duplicate_sample)

    print(f'Total generated duplicates for Test data: {duplicated_count}')
    
    # Shuffle the data to ensure random placement of red and blue wins
    random.shuffle(Simulation_Train)
    random.shuffle(Simulation_Test)
    
    # Print out the amount of data used
    print("AMOUNT OF DATA USING: ", len(Simulation_Train) + len(Simulation_Test))
    
    # Convert '0' and '1' strings to integers in Y and Y_test
    Y = np.array([int(simulation[0]) for simulation in Simulation_Train])
    Y_test = np.array([int(simulation[0]) for simulation in Simulation_Test])

    print(f"Training Data vs Testing Data: ({len(Simulation_Train)}, {len(Simulation_Test)}) ")
    print(
        f"Training Data - Amount RED Wins (Training vs Testing): ({len(np.where(Y == 0)[0])}, {len(np.where(Y == 1)[0])})")
    print(
        f"Testing Data - Amount BLUE Wins: (Training vs Testing): ({len(np.where(Y_test == 0)[0])}, {len(np.where(Y_test == 1)[0])})")
    return Simulation_Test, Simulation_Train

def fetch_simulation_games(number, gameboard_size, goBack, randomMoves):
    red_data = []  # List to collect "Red" results
    blue_data = []  # List to collect "Blue" results
    existing_games = set()
    removed = 0

    while len(red_data) < number or len(blue_data) < number:
        new_game = game.Game(gameboard_size)
        winner, feature, edges = new_game.SimulateGame(goBack, randomMoves)
        # Check if winner is Red or Blue
        if winner == "0" and len(red_data) < number:
            red_data.append((winner, feature, edges))
        elif winner == "1" and len(blue_data) < number:
            blue_data.append((winner, feature, edges))
    return red_data + blue_data

def createData(gameboard_size, csvName, number_of_examples, go_back, random_moves):
    if os.path.isfile(csvName + "_test_data.csv") or os.path.isfile(csvName + "_training_data.csv"):
        print("Dataset with the same name already exists!")
        print("Exiting...")
        exit()

    data = fetch_simulation_games(number=number_of_examples, gameboard_size=gameboard_size, goBack=go_back, randomMoves=random_moves)
    createCSV_noSimulation(data, csvName)
    test_data, training_data = filterData(simulation_data=data)
    createCSV_noSimulation(test_data, csvName+"_test_data")
    createCSV_noSimulation(training_data, csvName+"_training_data")
    print("Created dataset!")
