import os.path
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import data_generation

##############
# PARAMETERS #
##############
Gameboard_size = 3
Number_of_examples = 500
Go_back=0
Random_moves = True
CSV_name = f"{Gameboard_size}x{Gameboard_size}_goBack{Go_back}_set"

data_generation.createData(gameboard_size=Gameboard_size, csvName=CSV_name, number_of_examples=Number_of_examples, go_back=Go_back, random_moves=Random_moves)

    


