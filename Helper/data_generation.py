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
        field = ["winner", "feature"]
        writer.writerow(field)

        for i in range(examples):
            new_game = game.Game(board_size)
            winner, feature = new_game.SimulateGame(goBack)
            writer.writerow([winner, feature])


def createCSV_noSimulation(data, CSVname):
    with open(CSVname+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["winner", "feature"]
        writer.writerow(field)
        
        for i, da in enumerate(data):
            winner, feature = da
            writer.writerow([winner, feature])


def read_from_csv(filename):
    simulations = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            winner = int(row['winner'])
            features = eval(row['feature'])
            simulations.append([winner, features])
    return simulations

def filterData(simulation_data, log_file_name):
    with open(log_file_name, 'w') as file:
        file.write(f"AMOUNT OF DATA GENERATED: {len(simulation_data)}\n")

        red_wins = []
        blue_wins = []

        # Separate the simulation data into red and blue wins
        for simulation in simulation_data:
            winner = simulation[0]  # First element represents the winner
            if winner == "0":  # Red wins
                red_wins.append(simulation)
            elif winner == "1":  # Blue wins
                blue_wins.append(simulation)

        file.write(f"RED VS BLUE WINS: ({len(red_wins)}, {len(blue_wins)})\n")

        # Balance the number of red and blue wins
        num_red_wins = len(red_wins)
        num_blue_wins = len(blue_wins)
        red_samples = red_wins[:num_blue_wins]
        blue_samples = blue_wins

        file.write(f"RED SAMPLES vs BLUE SAMPLES: ({len(red_samples)}, {len(blue_samples)})\n")

        red_slice = int(0.9 * len(red_samples))
        blue_slice = int(0.9 * len(blue_samples))

        # Split into initial training and test sets
        train_red_sample = red_samples[:red_slice]
        train_blue_sample = blue_samples[:blue_slice]
        test_red_sample = red_samples[red_slice:]
        test_blue_sample = blue_samples[blue_slice:]

        # Combine red and blue wins for training data
        Simulation_Train = train_red_sample + train_blue_sample

        # Ensure no duplicates from training set in the test set
        training_set_keys = set((sim[0], tuple(sim[1])) for sim in Simulation_Train)
        Simulation_Test_Red = [
            sim for sim in test_red_sample
            if (sim[0], tuple(sim[1])) not in training_set_keys
        ]
        Simulation_Test_Blue = [
            sim for sim in test_blue_sample
            if (sim[0], tuple(sim[1])) not in training_set_keys
        ]

        # Ensure 1:1 ratio for red and blue wins in the test set
        desired_test_size = int(0.1 * len(simulation_data)) // 2  # Target size for each color

        file.write(f"Unique Test Red data: {len(Simulation_Test_Red)}\n")
        file.write(f"Unique Test Blue data: {len(Simulation_Test_Blue)}\n")
        file.write(f"Required duplications per color: {desired_test_size - len(Simulation_Test_Red)}\n")

        # Track duplications for each color
        red_duplicated_count = 0
        blue_duplicated_count = 0

        # Duplicate red wins if needed
        while len(Simulation_Test_Red) < desired_test_size:
            duplicate_sample = random.choice(Simulation_Test_Red)
            Simulation_Test_Red.append(duplicate_sample)
            red_duplicated_count += 1

        # Duplicate blue wins if needed
        while len(Simulation_Test_Blue) < desired_test_size:
            duplicate_sample = random.choice(Simulation_Test_Blue)
            Simulation_Test_Blue.append(duplicate_sample)
            blue_duplicated_count += 1

        # Combine balanced red and blue test sets
        Simulation_Test = Simulation_Test_Red + Simulation_Test_Blue
        random.shuffle(Simulation_Test)
        random.shuffle(Simulation_Train)

        file.write(f'Total generated duplicates for Test data - Red: {red_duplicated_count}, Blue: {blue_duplicated_count}\n')
        file.write(f"AMOUNT OF DATA USING: {len(Simulation_Train) + len(Simulation_Test)}\n")

        # Convert '0' and '1' strings to integers in Y and Y_test
        Y = np.array([int(simulation[0]) for simulation in Simulation_Train])
        Y_test = np.array([int(simulation[0]) for simulation in Simulation_Test])

        file.write(f"Training Data vs Testing Data: ({len(Simulation_Train)}, {len(Simulation_Test)})\n")
        file.write(
            f"Training Data - Amount RED Wins: {len(np.where(Y == 0)[0])}, BLUE Wins: {len(np.where(Y == 1)[0])}\n")
        file.write(
            f"Testing Data - Amount RED Wins: {len(np.where(Y_test == 0)[0])}, BLUE Wins: {len(np.where(Y_test == 1)[0])}\n")

    return Simulation_Test, Simulation_Train

def fetch_simulation_games(number, gameboard_size, goBack, randomMoves, maxMoves=None):
    red_data = []  # List to collect "Red" results
    blue_data = []  # List to collect "Blue" results
    existing_games = set()
    removed = 0
    counting = 0 

    while len(red_data) < number or len(blue_data) < number:
        new_game = game.Game(gameboard_size)
        winner, feature, moveList = new_game.SimulateGame(goBack, randomMoves)
        # Check the amount of moves
        if maxMoves is not None:
            if len(moveList) > maxMoves:
                continue
        # Check if winner is Red or Blue
        if winner == "0" and len(red_data) < number:
            red_data.append((winner, feature))
            counting += 1
        elif winner == "1" and len(blue_data) < number:
            blue_data.append((winner, feature))
            counting += 1
        print(f"Genered {counting}/{number*2} games")
    return red_data + blue_data

# The function you run to create data sets!!!
def createData(gameboard_size, csvName, number_of_examples, go_back, random_moves, maxMoves):
    if os.path.isfile(csvName + "_test_data.csv") or os.path.isfile(csvName + "_training_data.csv"):
        print("Dataset with the same name already exists!")
        print("Exiting...")
        exit()

    data = fetch_simulation_games(number=number_of_examples, gameboard_size=gameboard_size, goBack=go_back, randomMoves=random_moves, maxMoves=maxMoves)
    createCSV_noSimulation(data, csvName)
    test_data, training_data = filterData(simulation_data=data, log_file_name=csvName+"_data_generation_log.txt")
    createCSV_noSimulation(test_data, csvName+"_test_data")
    createCSV_noSimulation(training_data, csvName+"_training_data")
    print("Created dataset!")
