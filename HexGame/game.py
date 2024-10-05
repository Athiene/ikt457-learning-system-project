import random

class Game:

    # On initilize
    def __init__(self, size):
        self.board_size = size
        self.Player1 = True

        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = [[None] for _ in range(self.board_size * self.board_size)]

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell
        self.CellNodesEdgeList = [[] for _ in range(self.board_size * self.board_size)]

        # Array that contains a moves done
        self.MoveList = []
        return

    # BROKEN
    def NOTdfs(self, index, playerColor, visited, target_side_condition):

        # Perform DFS to check for continuous connections to the target side
        if index in visited:
            return False

        visited.add(index)

        # Check if this cell reaches the target side (for Red: bottom, for Blue: right)
        if target_side_condition(index):
            return True

        # Explore connected nodes for the current player
        for neighbor in self.CellNodesEdgeList[index]:
            if self.CellNodesFeatureList[neighbor] == playerColor:
                if self.dfs(neighbor, playerColor, visited, target_side_condition):
                    return True
        return False

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
                    return "Red"

        # Check for Blue (from left to right)
        for index in range(0, self.board_size * self.board_size, self.board_size):
            if self.CellNodesFeatureList[index] == "Blue":
                visited = set()
                if self.dfs(index, "Blue", visited, lambda i: i % self.board_size == (self.board_size - 1)):
                    return "Blue"
        return None

    # BROKEN
    def NOTconnectionCheck(self, index):
        playerColor = self.CellNodesFeatureList[index]

        if (index > self.board_size):
            # Checks cells from the row above for connections
            if playerColor == self.CellNodesFeatureList[index - self.board_size]:
                self.CellNodesEdgeList[index].append(index - self.board_size)
                self.CellNodesEdgeList[index - self.board_size].append(index)

            if playerColor == self.CellNodesFeatureList[(index - self.board_size) + 1]:
                self.CellNodesEdgeList[index].append((index - self.board_size) + 1)
                self.CellNodesEdgeList[(index - self.board_size) + 1].append(index)

        if (index < (self.board_size * (self.board_size - 1))):
            # Checks cells from the row under for connections
            if playerColor == self.CellNodesFeatureList[index + self.board_size]:
                self.CellNodesEdgeList[index].append(index + self.board_size)
                self.CellNodesEdgeList[index + self.board_size].append(index)

            if playerColor == self.CellNodesFeatureList[(index + self.board_size) - 1]:
                self.CellNodesEdgeList[index].append((index + self.board_size) - 1)
                self.CellNodesEdgeList[(index + self.board_size) - 1].append(index)

        # Checks cells on its right for connection
        if index != ((self.board_size * self.board_size) - 1) and playerColor == self.CellNodesFeatureList[index + 1]:
            self.CellNodesEdgeList[index].append(index + 1)
            self.CellNodesEdgeList[index + 1].append(index)

        # Checks cells on its left for connection
        if index != 0 and playerColor == self.CellNodesFeatureList[index - 1]:
            self.CellNodesEdgeList[index].append(index - 1)
            self.CellNodesEdgeList[index - 1].append(index)
        return

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
        if winner == "Red" or winner == "Blue":
            print(f"{winner} has won the game!")
            return True

        return False

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
        print(game.CellNodesFeatureList)
        print()
        print("Connectons for cells")
        print(game.CellNodesEdgeList)
        print()
        print("Moves done")
        print(game.MoveList)
        print()
        self.print_hex_diagram()

    def RandomAvailableCell(self):
        # Create a list of all valid (x, y) coordinates where the cell is [None]
        none_cells = [i for i, cell in enumerate(self.CellNodesFeatureList) if cell == [None]]

        # Selects a random cell from all of the available cells
        index = random.choice(none_cells)
        return index

    def returnTurns(self, goBack):
        if goBack == 0:
            return

        for i in range(goBack):
            # Removes the last index from MoveList
            lastIndex = self.MoveList.pop()

            # Removes any player feature at index lastIndex and sets it to [None]
            self.CellNodesFeatureList[lastIndex] = [None]

            # Clear any connections related to lastIndex
            for edges in self.CellNodesEdgeList:
                if lastIndex in edges:
                    edges.remove(lastIndex)

            # Clear the edge list for the lastIndex
            self.CellNodesEdgeList[lastIndex] = []

        return

    def SimulateGame(self, goBack):
        condition = True
        while condition:
            hasWinner = self.makeMove(True, self.RandomAvailableCell())
            if hasWinner:
                condition = False
        game.print_overview()
        self.returnTurns(goBack)
        return self.CellNodesFeatureList, self.CellNodesEdgeList


for i in range(1):
    print(f"###### GAME {i + 1} #######")
    game = Game(6)
    newGame = game.SimulateGame(1)
    featureList, connectinList = newGame
    print("##### After Removal ######")
    game.print_hex_diagram()
    print()
    print("Features: ")
    print(featureList)
    print()
    print("Connections: ")
    print(connectinList)
    print()

# game.print_overview()

