from random import choice

from fontTools.subset import intersect
from numba.cpython.setobj import EMPTY
from numpy.matlib import empty


class BP:


    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list, move_list, red_bp, blue_bp , red_paths, All_Edges):
        self.board_size = size
        self.Player1 = True
        self.Winner = None

        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = cell_node_feature_list

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell with the same symbol
        self.CellNodesEdgeList = cell_nodes_edge_list




        self.all_edges = All_Edges



        # Array that contains a moves done
        self.MoveList = move_list

        # Array that contains the possible bridges
        self.PossibleBridgesList = [[] for _ in range(self.board_size * self.board_size)]

        self.Red_Bp_Edges = [[] for _ in range(self.board_size * self.board_size)]

        self.Blue_Bp_Edges = [[] for _ in range(self.board_size * self.board_size)]

        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]


        # Initialize Red_Bp and Blue_Bp as lists of lists
        self.Red_Bp = red_bp

        self.Blue_Bp = blue_bp

        self.Red_Paths = red_paths



        return



    def get_next_move(self):
        index = None

        if len(self.MoveList) < 2:
            print("\nGetNextMove: Both players need to make at least one move")
            return None

        # Set the current position to the opponent's last move
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        print(f"Current Position being evaluated: {current_position} for {playerColor} ")

        index = self.evaluate_bridge()

        self.store_bp_index(index)

        #self.find_all_path()

        self.find_paths()

        print("")



        """
        # Step 1: Detect possible bridges for the current position
        self.detect_bridge(current_position)

        # Step 2: Find the highest index from detected bridges
        bridge_patterns = self.PossibleBridgesList[current_position]

        print(f"Bridge Patterns for {current_position}: {bridge_patterns}")

        if bridge_patterns:
            # Find and set the highest index from the list of possible bridges
            index = max(bridge_patterns)
        """
        # Return the highest index as the next move, or None if no bridges are available
        return index

    def find_paths(self):

        #Gets all the red indexes from CellNodesFeatureList
        red_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Red"]
        print("All the red indexes in CellNodeFeatureList are at:")
        print(red_indexes)

        #Initialize red_edges_mapping to store edges for each red index
        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]
        self.Red_Paths = [[]]

        # Populate red_edges_mapping with a flat list of edges for each red index
        for red_index in red_indexes:
            red_edges = self.all_edges[red_index]
            # Direct assignment to ensure it's a flat list of edges, not a nested list
            self.red_edges_mapping[red_index] = list(red_edges)  # Ensure a flat list


        # Debugging output to confirm structure
        print("\nRed indexes with their edges: ")
        for index, edges in enumerate(self.red_edges_mapping):
            if edges:  # Print only non-empty entries for clarity
                print(f"Index {index}: {edges}")


        # Check for paths between each pair of red nodes
        print("\nPaths between red nodes:")

        for i, red_index in enumerate(red_indexes):
            edges_for_index_i = set(self.red_edges_mapping[red_index])  # Convert to set for comparison
            print(f"\nCurrent Position being evaluated: {red_index} for Red")
            print(f"Edges for red index {red_index}: {edges_for_index_i}")


            # Compare with subsequent red indexes
            for j in range( len(red_indexes)):
                next_red_index = red_indexes[j]
                edges_for_next_index = set(self.red_edges_mapping[next_red_index])

                # Find common edges
                common_edges = edges_for_index_i.intersection(edges_for_next_index)
                if [next_red_index, red_index] not in self.Red_Paths and [red_index, next_red_index] not in self.Red_Paths:

                    # Check if there are at least two common edges
                    if len(common_edges) == 2:
                        print(
                            f"Path exists between red index {red_index} and red index {next_red_index} with common edges: {common_edges}")
                        path_found = False
                        for path in self.Red_Paths:
                            if red_index in path or next_red_index in path:
                                # Extend the existing path with any new unique nodes
                                if red_index not in path:
                                    path.append(red_index)
                                if next_red_index not in path:
                                    path.append(next_red_index)
                                path_found = True
                                break

                        # If neither index is in any existing path, create a new path
                        if not path_found:
                            self.Red_Paths.append([red_index, next_red_index])

        # Final output of all unique paths
        print("\nFinal Red paths with unique pairs:")
        print(self.Red_Paths)
    """
    #This function evaluates all the detected bridges and chooses the best one for the specified color
    def find_all_path(self) :
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        if self.CellNodesFeatureList[current_position] == "Red":

            for red_moves in self.MoveList:
                red_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Red"]
                if red_moves in red_indexes:
                        print(f"Match found: Index {red_moves} is both in move list and marked as 'Red' in CellNodesFeatureList")

                    # Up connection
                        if red_moves >= self.board_size and (red_moves - self.board_size) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves - self.board_size)

                        # Up-right connection
                        if red_moves >= self.board_size and red_moves % self.board_size != (self.board_size - 1) and (
                                red_moves - self.board_size + 1) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves - self.board_size + 1)

                        # Down connection
                        if red_moves < self.board_size * (self.board_size - 1) and (red_moves + self.board_size) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves + self.board_size)

                        # Down-left connection
                        if red_moves < self.board_size * (self.board_size - 1) and red_moves % self.board_size != 0 and (
                                red_moves + self.board_size - 1) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves + self.board_size - 1)

                        # Right connection
                        if red_moves % self.board_size != (self.board_size - 1) and (red_moves + 1) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves + 1)

                        # Left connection
                        if red_moves % self.board_size != 0 and (red_moves - 1) not in self.Red_Bp_Edges[red_moves]:
                            self.Red_Bp_Edges[red_moves].append(red_moves - 1)

                        print()
                        print("Edges for the index in Red_Bp")
                        print(self.Red_Bp_Edges)

        if self.CellNodesFeatureList[current_position] == "Blue":
            for blue_moves in self.MoveList:
                blue_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Blue"]
                if blue_moves in blue_indexes:
                        print(f"Match found: Index {blue_moves} is both in move list and marked as 'Blue' in CellNodesFeatureList")

                    # Up connection
                        if blue_moves >= self.board_size and (blue_moves - self.board_size) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves - self.board_size)

                        # Up-right connection
                        if blue_moves >= self.board_size and blue_moves % self.board_size != (self.board_size - 1) and (
                                blue_moves - self.board_size + 1) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves - self.board_size + 1)

                        # Down connection
                        if blue_moves < self.board_size * (self.board_size - 1) and (blue_moves + self.board_size) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves + self.board_size)

                        # Down-left connection
                        if blue_moves < self.board_size * (self.board_size - 1) and blue_moves % self.board_size != 0 and (
                                blue_moves + self.board_size - 1) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves + self.board_size - 1)

                        # Right connection
                        if blue_moves % self.board_size != (self.board_size - 1) and (blue_moves + 1) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves + 1)

                        # Left connection
                        if blue_moves % self.board_size != 0 and (blue_moves - 1) not in self.Blue_Bp_Edges[blue_moves]:
                            self.Blue_Bp_Edges[blue_moves].append(blue_moves - 1)
    """


    def evaluate_bridge(self):

        index = None

        current_position = self.MoveList[-2]

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":
                # Prioritize patterns near the wall for Red
                wall_patterns = [bp for bp in bridge_patterns if self.is_near_wall(bp)]

                # First check if any wall-adjacent patterns are available and select one
                if wall_patterns:
                    index = choice(wall_patterns)
                    print(f"Red selected wall-adjacent index: {index}")
                else:
                    # Distance of detected bp from current position
                    distances = [(x, abs(x - current_position)) for x in bridge_patterns]

                    # Find the longest distance from current position regardless of if its over or under the current
                    max_distance = max(distances, key=lambda x: x[1])[1]

                    # Get all bridge patterns that are at the maximum distance

                    farthest_patterns = [x[0] for x in distances if x[1] == max_distance]

                    # Randomly select between the highest and lowest of the farthest patterns
                    index = choice([max(farthest_patterns)])
                    print(f"Red selected farthest index: {index}")



            if self.CellNodesFeatureList[current_position] == "Blue":

                # Minimum distance to current_position
                min_distance = min(abs(x - current_position) for x in bridge_patterns)

                # Al bp that are minimum positions
                closest_patterns = [x for x in bridge_patterns if abs(x - current_position) == min_distance]

                # If multiple patterns are closest, pick one at random
                index = choice(closest_patterns)


        #When a possible brige pattern index has been used, remove from the PossibleBridgeList
        for sublist in self.PossibleBridgesList:
            if index in sublist:
                sublist.remove(index)
        print(f"Removed {index} from all sublists in PossibleBridgesList")


        return index




    def store_bp_index(self, index):
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]


        if playerColor == "Red":
            if index is not None:
                print(f"Appending {index} to Red_Bp at position")  # Debug statement
                self.Red_Bp.append(index)
                self.CellNodesFeatureList[index] = "Red"
                # Optionally, append to the list of red indexes if you maintain such a list
                print("Red bridge pattern indexes: ", self.Red_Bp)  # Shows the entire Red_Bp structure

        if playerColor == "Blue":
            if self.Red_Bp is not None:
                print(f"Blue selected index: {index}")
                print(f"Appending {index} to Red_Bp at position")  # Debug statement
                if index != "None":
                    self.Blue_Bp.append(index)
                    print("Blue bridge pattern indexes: ", self.Blue_Bp)  # Shows the entire Red_Bp structure


    def check_top_bottom_wall(self, index):
        if index < self.board_size:
            print(f"Index {index} is touching the top wall.")
        elif index >= self.board_size * (self.board_size - 1):

            print(f"Index {index} is touching the bottom wall.")


    def is_near_wall(self, index):
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        if playerColor == "red":
            # Check if index is on the top or bottom edge for red
            if index < self.board_size:  # Top edge
                return True
            elif index >= self.board_size * (self.board_size - 1):  # Bottom edge
                return True

        if playerColor == "blue":
            # Check if index is on the left or right edge for blue
            if index % self.board_size == 0:  # Left edge
                return True
            elif index % self.board_size == (self.board_size - 1):  # Right edge
                return True

        return False

    def detect_bridge(self, index):
        playerColor = self.CellNodesFeatureList[index]
        board_size = self.board_size

        # Check if the most upper bridge pattern is possible
        if index >= 2 * board_size:
            # Ensure the index is not on the right wall before considering a top-right bridge pattern
            bp_top_index = (index - 2 * board_size + 1)
            top_r_index = (index - board_size + 1)
            top_l_index = (index - board_size)

            if (0 <= bp_top_index < len(self.CellNodesFeatureList) and
                    0 <= top_r_index < len(self.CellNodesFeatureList) and
                    0 <= top_l_index < len(self.CellNodesFeatureList) and
                    index % board_size != board_size - 1):  # Ensure index is not on the right edge
                if (self.CellNodesFeatureList[bp_top_index] == "None" and
                        self.CellNodesFeatureList[top_r_index] == "None" and
                        self.CellNodesFeatureList[top_l_index] == "None"):
                    self.PossibleBridgesList[index].append(bp_top_index)





        # Check if upper right bridge pattern is possible
        if index >= board_size and index % self.board_size != (self.board_size - 1):  # Ensure not at right edge
            bp_top_right_index = (index - self.board_size + 2)
            up_l_index = (index - self.board_size + 1)
            up_r_index = (index + 1)

            if (0 <= bp_top_right_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_index < len(self.CellNodesFeatureList) and
                    0 <= up_r_index < len(self.CellNodesFeatureList) and
                    index % self.board_size != (self.board_size - 2)):  # Ensure not at right edge

                if self.CellNodesFeatureList[bp_top_right_index] == "None" and self.CellNodesFeatureList[
                    up_l_index] == "None" and self.CellNodesFeatureList[up_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_right_index)



        # Check if the upper left bridge pattern is possible
        if index >= board_size and index % board_size > 0:  # Ensure index is not in the first column
            bp_top_left_index = (index - board_size - 1)
            up_l_up_index = (index - board_size)
            up_l_down_index = (index - 1)

            if (0 <= bp_top_left_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_up_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_down_index < len(self.CellNodesFeatureList)):
                if (self.CellNodesFeatureList[bp_top_left_index] == "None" and
                        self.CellNodesFeatureList[up_l_up_index] == "None" and
                        self.CellNodesFeatureList[up_l_down_index] == "None"):
                    self.PossibleBridgesList[index].append(bp_top_left_index)


        # Check if most down bridge pattern is possible
        if index >= -2 * board_size:
            # the two row above index & the above and above-right index
            bp_bot_index = (index + 2 * self.board_size - 1)
            bot_r_index = (index + self.board_size - 1)
            bot_l_index = (index + self.board_size)

            if (0 <= bp_bot_index < len(self.CellNodesFeatureList) and
                    0 <= bot_r_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_index < len(self.CellNodesFeatureList) and
                    index % self.board_size != (self.board_size + 2)):

                # if all the cells needed for bridge pattern for current index is empty, the hex index to make the bridge pattern is appended in a list
                if self.CellNodesFeatureList[bp_bot_index] == "None" and self.CellNodesFeatureList[
                    bot_r_index] == "None" and self.CellNodesFeatureList[bot_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_index)

        # Check if the bottom right bridge pattern is possible
        if index < board_size * (board_size - 1) and index % board_size != board_size - 1:
            bp_bot_right_index = (index + board_size + 1)
            bot_l_index = (index + board_size)
            bot_r_index = (index + 1)

            if (0 <= bp_bot_right_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_index < len(self.CellNodesFeatureList) and
                    0 <= bot_r_index < len(self.CellNodesFeatureList)):
                if (self.CellNodesFeatureList[bp_bot_right_index] == "None" and
                        self.CellNodesFeatureList[bot_l_index] == "None" and
                        self.CellNodesFeatureList[bot_r_index] == "None"):
                    self.PossibleBridgesList[index].append(bp_bot_right_index)

        # Check if the bottom left bridge pattern is possible
        if index < board_size * (board_size - 1) and index % board_size > 0:  # Ensure index is not in the first column
            bp_bot_left_index = (index + board_size - 2)
            bot_l_down_index = (index + board_size - 1)
            bot_l_up_index = (index - 1)

            if (0 <= bp_bot_left_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_up_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_down_index < len(self.CellNodesFeatureList)):
                if (self.CellNodesFeatureList[bp_bot_left_index] == "None" and
                        self.CellNodesFeatureList[bot_l_up_index] == "None" and
                        self.CellNodesFeatureList[bot_l_down_index] == "None"):
                    self.PossibleBridgesList[index].append(bp_bot_left_index)









