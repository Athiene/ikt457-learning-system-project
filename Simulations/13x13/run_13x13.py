import argparse
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Helper import main

gameboard_size = 13
Go_back = 0
csvName = f"{gameboard_size}x{gameboard_size}_goBack{Go_back}_set"

def default_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", default=200, type=int)
    parser.add_argument("--number-of-clauses", default=2000, type=int)
    parser.add_argument("--T", default=2000, type=int)
    parser.add_argument("--s", default=1.2, type=float)
    parser.add_argument("--depth", default=3, type=int)
    parser.add_argument("--hypervector-size", default=1024, type=int)
    parser.add_argument("--hypervector-bits", default=2, type=int)
    parser.add_argument("--message-size", default=1024, type=int)
    parser.add_argument("--message-bits", default=2, type=int)
    parser.add_argument("--number-of-examples", default=50000, type=int)
    parser.add_argument('--double-hashing', dest='double_hashing', default=False, action='store_true')
    parser.add_argument("--max-included-literals", default=169, type=int)

    args = parser.parse_args()
    for key, value in kwargs.items():
        if key in args.__dict__:
            setattr(args, key, value)
    return args

main.Main(gameboard_size=gameboard_size,Go_back=Go_back, csvName=csvName, Args=default_args())

