import os.path
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import data_generation

##############
# PARAMETERS #
##############
Gameboard_size = 3
# This will be 2x, so if you write 1000, it will be 2000 number of examples
Number_of_examples = 1000
Go_back=0
Random_moves = False
CSV_name = f"SM_{Gameboard_size}x{Gameboard_size}_goBack{Go_back}_set"
if Random_moves:
    CSV_name = f"RM_{Gameboard_size}x{Gameboard_size}_goBack{Go_back}_set"

data_generation.createData(gameboard_size=Gameboard_size, csvName=CSV_name, number_of_examples=Number_of_examples, go_back=Go_back, random_moves=Random_moves, maxMoves=0)

    


