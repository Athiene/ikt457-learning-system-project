import csv
import os.path
import sys
import os 
import random
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import plotting
from HexGame import game
from scipy.stats import skewnorm
import matplotlib.pyplot as plt

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
        file.write("===== Before Data Handling =====\n")
        file.write(f"AMOUNT OF DATA GENERATED: {len(simulation_data)}\n")

        red_wins = []
        blue_wins = []

        # Separate the simulation data into red and blue wins
        for simulation in simulation_data:
            winner = simulation[0]  # First element represents the winner
            if winner == "0":
                red_wins.append(simulation)
            elif winner == "1":
                blue_wins.append(simulation)

        file.write(f"RED VS BLUE WINS: ({len(red_wins)}, {len(blue_wins)})\n")

        # Calculate required sizes for training and test datasets
        total_data = len(simulation_data)
        test_size = int(0.1 * total_data)
        train_size = total_data - test_size

        # Ensure equal splits for Red and Blue
        test_size_per_color = test_size // 2
        train_size_per_color = train_size // 2

        # Prepare test datasets
        test_red_sample = red_wins[:test_size_per_color]
        test_blue_sample = blue_wins[:test_size_per_color]

        # Remove test samples from the remaining data
        test_set_keys = set((sim[0], tuple(sim[1])) for sim in test_red_sample + test_blue_sample)
        remaining_red = [sim for sim in red_wins if (sim[0], tuple(sim[1])) not in test_set_keys]
        remaining_blue = [sim for sim in blue_wins if (sim[0], tuple(sim[1])) not in test_set_keys]

        file.write("\n===== After Data Handling =====\n")
        # Log removed duplicates from training dataset
        removed_from_training = len(red_wins) + len(blue_wins) - len(remaining_red) - len(remaining_blue)
        file.write(f"Duplicates removed from Training dataset: {removed_from_training}\n")

        # Duplicate Red wins for training if needed
        train_red_sample = remaining_red[:train_size_per_color]
        red_duplicated_count = 0
        while len(train_red_sample) < train_size_per_color:
            duplicate_sample = random.choice(train_red_sample)
            train_red_sample.append(duplicate_sample)
            red_duplicated_count += 1

        # Duplicate Blue wins for training if needed
        train_blue_sample = remaining_blue[:train_size_per_color]
        blue_duplicated_count = 0
        while len(train_blue_sample) < train_size_per_color:
            duplicate_sample = random.choice(train_blue_sample)
            train_blue_sample.append(duplicate_sample)
            blue_duplicated_count += 1

        # Duplicate Red wins for test if needed
        test_red_duplicated_count = 0
        while len(test_red_sample) < test_size_per_color:
            duplicate_sample = random.choice(test_red_sample)
            test_red_sample.append(duplicate_sample)
            test_red_duplicated_count += 1

        # Duplicate Blue wins for test if needed
        test_blue_duplicated_count = 0
        while len(test_blue_sample) < test_size_per_color:
            duplicate_sample = random.choice(test_blue_sample)
            test_blue_sample.append(duplicate_sample)
            test_blue_duplicated_count += 1

        # Combine training and test datasets
        Simulation_Train = train_red_sample + train_blue_sample
        Simulation_Test = test_red_sample + test_blue_sample

        # Shuffle datasets
        random.shuffle(Simulation_Train)
        random.shuffle(Simulation_Test)

        # Validate no overlap
        training_set_keys = set((sim[0], tuple(sim[1])) for sim in Simulation_Train)
        test_set_overlap = [
            sim for sim in Simulation_Test
            if (sim[0], tuple(sim[1])) in training_set_keys
        ]
        file.write(f"Overlap between training and test datasets: {len(test_set_overlap)}\n")
        assert len(test_set_overlap) == 0, "Overlap detected between training and test datasets!"

        # Log details
        file.write(f"Test dataset size: {len(Simulation_Test)}\n")
        file.write(f"Training dataset size: {len(Simulation_Train)}\n")
        file.write(f"Test size (Red): {len(test_red_sample)}, Test size (Blue): {len(test_blue_sample)}\n")
        file.write(f"Train size (Red): {len(train_red_sample)}, Train size (Blue): {len(train_blue_sample)}\n")
        file.write(f"Duplications generated in Test dataset - Red: {test_red_duplicated_count}, Blue: {test_blue_duplicated_count}\n")
        file.write(f"Duplications generated in Train dataset - Red: {red_duplicated_count}, Blue: {blue_duplicated_count}\n")
        
        # Log internal duplicates
        unique_train_games = len(set((sim[0], tuple(sim[1])) for sim in Simulation_Train))
        unique_test_games = len(set((sim[0], tuple(sim[1])) for sim in Simulation_Test))
        training_internal_duplicates = len(Simulation_Train) - unique_train_games
        testing_internal_duplicates = len(Simulation_Test) - unique_test_games
        file.write(f"Internal duplicates in Training dataset: {training_internal_duplicates}\n")
        file.write(f"Internal duplicates in Testing dataset: {testing_internal_duplicates}\n")

        # Log unique game counts
        file.write(f"Unique games in Training dataset: {unique_train_games}\n")
        file.write(f"Unique games in Testing dataset: {unique_test_games}\n")

        # Convert '0' and '1' strings to integers in Y and Y_test
        Y = np.array([int(simulation[0]) for simulation in Simulation_Train])
        Y_test = np.array([int(simulation[0]) for simulation in Simulation_Test])

        file.write(f"Training Data - Amount RED Wins: {len(np.where(Y == 0)[0])}, BLUE Wins: {len(np.where(Y == 1)[0])}\n")
        file.write(f"Testing Data - Amount RED Wins: {len(np.where(Y_test == 0)[0])}, BLUE Wins: {len(np.where(Y_test == 1)[0])}\n")

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
            if goBack > 0:
                if len(moveList) > maxMoves-goBack:
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
