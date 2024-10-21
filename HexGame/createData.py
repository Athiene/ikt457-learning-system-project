import csv
from HexGame import game

def createCSV(board_size, examples, goBack, CSVname):
    with open(CSVname+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["winner", "feature", "edges"]

        for i in range(examples):
            new_game = game.Game(board_size)
            winner, feature, edges = new_game.SimulateGame(goBack)
            writer.writerow(field)
            writer.writerow([winner, feature, edges])


createCSV(board_size=3,examples=10,goBack=0,CSVname="3x3_set")