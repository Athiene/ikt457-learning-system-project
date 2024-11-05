import random
from .bridge_pattern import BP

class Game:

    # On initilize
    def __init__(self, size):
        self.board_size = size
        self.Player1 = True
        self.Winner = None

        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = ["None" for _ in range(self.board_size * self.board_size)]

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell with the same symbol
        self.CellNodesEdgeList = [[] for _ in range(self.board_size * self.board_size)]

        # Creates an array containing arrays
        # A single array in the array represents all of the connections of a cell
        self.all_edges = [[] for _ in range(self.board_size * self.board_size)]
        self.findAllEdges()

        # Array that contains a moves done
        self.MoveList = []

        self.Red_Bp = []

        self.Blue_Bp = []

        # Stores the maximum number of edges for each node
        self.maxEdgesPerNode = [0 for _ in range(self.board_size * self.board_size)]
        self.calculateMaxEdges()
        return

    def findAllEdges(self):
        for index in range(self.board_size * self.board_size):
            # Up connection
            if index >= self.board_size and (index - self.board_size) not in self.all_edges[index]:
                self.all_edges[index].append(index - self.board_size)
                self.all_edges[index - self.board_size].append(index)

            # Up-right connection
            if index >= self.board_size and index % self.board_size != (self.board_size - 1) and (
                    index - self.board_size + 1) not in self.all_edges[index]:
                self.all_edges[index].append(index - self.board_size + 1)
                self.all_edges[index - self.board_size + 1].append(index)

            # Down connection
            if index < self.board_size * (self.board_size - 1) and (index + self.board_size) not in self.all_edges[index]:
                self.all_edges[index].append(index + self.board_size)
                self.all_edges[index + self.board_size].append(index)

            # Down-left connection
            if index < self.board_size * (self.board_size - 1) and index % self.board_size != 0 and (
                    index + self.board_size - 1) not in self.all_edges[index]:
                self.all_edges[index].append(index + self.board_size - 1)
                self.all_edges[index + self.board_size - 1].append(index)

            # Right connection
            if index % self.board_size != (self.board_size - 1) and (index + 1) not in self.all_edges[index]:
                self.all_edges[index].append(index + 1)
                self.all_edges[index + 1].append(index)

            # Left connection
            if index % self.board_size != 0 and (index - 1) not in self.all_edges[index]:
                self.all_edges[index].append(index - 1)
                self.all_edges[index - 1].append(index)

    def calculateMaxEdges(self):
        for index in range(self.board_size * self.board_size):
            # Up connections
            if index >= self.board_size:
                self.maxEdgesPerNode[index] += 1  # Directly above
                if index % self.board_size != (self.board_size - 1):
                    self.maxEdgesPerNode[index] += 1  # Up-right

            # Down connections
            if index < self.board_size * (self.board_size - 1):
                self.maxEdgesPerNode[index] += 1  # Directly below
                if index % self.board_size != 0:
                    self.maxEdgesPerNode[index] += 1  # Down-left

            # Left and right connections
            if index % self.board_size != (self.board_size - 1):
                self.maxEdgesPerNode[index] += 1  # Directly to the right
            if index % self.board_size != 0:
                self.maxEdgesPerNode[index] += 1  # Directly to the left

    def print_max_edges(self):
        for i in range(self.board_size):
            row = self.maxEdgesPerNode[i * self.board_size:(i + 1) * self.board_size]
            print(f"Row {i}: {row}")


    def dfs(self, index, playerColor, visited, target_side_condition):
        # If already visited return false
        if index in visited:
            return False

        visited.add(index)

        # Check if this cell reaches the target side: If blue, then rightside
        if target_side_condition(index):
            return True

        # Explore neighbors
        for neighbor in self.CellNodesEdgeList[index]:
            if self.CellNodesFeatureList[neighbor] == playerColor and neighbor not in visited:
                if self.dfs(neighbor, playerColor, visited, target_side_condition):
                    return True

        return False

    # Checks for winner
    def winnerCheck(self):
        # Check for Red (from top to bottom)
        for index in range(self.board_size):
            if self.CellNodesFeatureList[index] == "Red":
                visited = set()
                if self.dfs(index, "Red", visited, lambda i: i >= (self.board_size * (self.board_size - 1))):
                    return "0"

        # Check for Blue (from left to right)
        for index in range(0, self.board_size * self.board_size, self.board_size):
            if self.CellNodesFeatureList[index] == "Blue":
                visited = set()
                if self.dfs(index, "Blue", visited, lambda i: i % self.board_size == (self.board_size - 1)):
                    return "1"
        return None

    # Check cells for connections
    def connectionCheck(self, index):
        playerColor = self.CellNodesFeatureList[index]

        # Up connection
        if index >= self.board_size:
            if playerColor == self.CellNodesFeatureList[index - self.board_size]:
                self.CellNodesEdgeList[index].append(index - self.board_size)
                self.CellNodesEdgeList[index - self.board_size].append(index)

            if index % self.board_size != (self.board_size - 1) and playerColor == self.CellNodesFeatureList[
                index - self.board_size + 1]:
                # Up-right
                self.CellNodesEdgeList[index].append(index - self.board_size + 1)
                self.CellNodesEdgeList[index - self.board_size + 1].append(index)

        # Down  connection
        if index < self.board_size * (self.board_size - 1):
            if playerColor == self.CellNodesFeatureList[index + self.board_size]:
                self.CellNodesEdgeList[index].append(index + self.board_size)
                self.CellNodesEdgeList[index + self.board_size].append(index)

            if index % self.board_size != 0 and playerColor == self.CellNodesFeatureList[index + self.board_size - 1]:
                # Down-left
                self.CellNodesEdgeList[index].append(index + self.board_size - 1)
                self.CellNodesEdgeList[index + self.board_size - 1].append(index)

        # Right connection
        if index % self.board_size != (self.board_size - 1) and playerColor == self.CellNodesFeatureList[index + 1]:
            self.CellNodesEdgeList[index].append(index + 1)
            self.CellNodesEdgeList[index + 1].append(index)

        # Left connection
        if index % self.board_size != 0 and playerColor == self.CellNodesFeatureList[index - 1]:
            self.CellNodesEdgeList[index].append(index - 1)
            self.CellNodesEdgeList[index - 1].append(index)

    # Makes random move
    def makeMove(self, option, index):

        # Changes the cells to corresponding player color: Red or Blue
        if self.Player1:
            self.CellNodesFeatureList[index] = "Red"
            self.Player1 = False
        else:
            self.CellNodesFeatureList[index] = "Blue"
            self.Player1 = True

        # Append the move (index) in MoveList
        self.MoveList.append(index)

        # Checks if the move made creates any connections
        self.connectionCheck(index)

        if option == True:
            # Print current hex diagram
            self.print_hex_diagram()

        # Check if there's a winner after the move
        winner = self.winnerCheck()
        if winner == "1" or winner == "0":
            # print(f"{winner} has won the game!")
            return winner

        return None


    def print_hex_diagram(self):
        print()
        print(f"Iteration: {len(self.MoveList)}")
        print()
        for i in range(self.board_size):
            # Indent every other row for the hex effect
            indent = ' ' * i
            row = self.CellNodesFeatureList[i * self.board_size:(i + 1) * self.board_size]
            # Format the row for display

            formatted_row = ' '.join([str(cell[0]) if cell[0] else '.' for cell in row])
            print(f"{indent}{formatted_row}")

    def print_overview(self):
        print()
        print("Features for cells")
        print(self.CellNodesFeatureList)
        print()
        print("Connectons for cells")
        print(self.CellNodesEdgeList)
        print()
        print("Moves done")
        print(self.MoveList)
        print()
        print("----")


        self.print_hex_diagram()

    def RandomAvailableCell(self):
        # Create a list of all valid (x, y) coordinates where the cell is "None"
        none_cells = [i for i, cell in enumerate(self.CellNodesFeatureList) if cell == "None"]

        # Selects a random cell from all of the available cells
        index = random.choice(none_cells)
        return index

    def returnTurns(self, goBack, option):
        if goBack == 0:
            return

        for i in range(goBack):
            # Removes the last index from MoveList
            lastIndex = self.MoveList.pop()

            # Removes any player feature at index lastIndex and sets it to "None"
            self.CellNodesFeatureList[lastIndex] = "None"

            # Clear any connections related to lastIndex
            for edges in self.CellNodesEdgeList:
                if lastIndex in edges:
                    edges.remove(lastIndex)

            # Clear the edge list for the lastIndex
            self.CellNodesEdgeList[lastIndex] = []

            if option:
                print("##### After Removal ######")
                self.print_hex_diagram()
                print()
                print("Features: ")
                print(self.CellNodesFeatureList)
                print()
                print("Connections: ")
                print(self.CellNodesEdgeList)
                print()


        return

    def SimulateGame(self, goBack, randomMoves):
        print("SimulateGame started")  # Debug print to confirm function call
        condition = True

        while condition:
            # Options: (1) Random moves (2) Strategy based moves
            if randomMoves:
                self.Winner = self.makeMove(False, self.RandomAvailableCell())
            else:
                bp = BP(self.board_size, self.CellNodesFeatureList, self.CellNodesEdgeList, self.MoveList , self.Red_Bp, self.Blue_Bp)
                move = bp.get_next_move()
                if move is None:
                    # Fallback to a random move if no bridge move is available
                    self.Winner = self.makeMove(False, self.RandomAvailableCell())
                else:
                    # Execute the selected bridge move
                    self.Winner = self.makeMove(False, move)
            # Checks Winner is not None to break out of loop
            if self.Winner is not None:
                condition = False

        self.returnTurns(goBack, False)
        return self.Winner, self.CellNodesFeatureList, self.all_edges
