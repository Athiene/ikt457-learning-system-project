from random import choice

from fontTools.subset import intersect
from jinja2.nodes import Break
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

        #check if there are enough moves to proceed, if there are enough moves, continues to steps
        if len(self.MoveList) < 2:
            print("\nget_next_move: Both players need to make at least one move")
            return None

        # Generate all possible paths so far (to get the dirst two random hexes with the paths
        self.find_paths_NO_PRINT()


        # Set the current position to the my last move to make a good current move
        current_position = self.MoveList[-2]

        # Get player color rn
        playerColor = self.CellNodesFeatureList[current_position]

        print(f"get_next_move: ______________________________________________________________________________-")

        print(f"get_next_move: Current Position being evaluated: {current_position} for {playerColor} ")


        # Step 1: select index by evaluation bridge
        index = self.check_if_neigbour_is_with_wakll()

        # Ensure selected index is marked in CellNodesFeatureList
        if index is not None:
            self.CellNodesFeatureList[index] = "Red"  # Mark index as occupied by Red
            self.MoveList.append(index)  # Optionally append to MoveList
            print(f"get_next_move: Marked index {index} as Red and updated MoveList.")


        print("get_next_move: now find paths functtion will happen: ")
        # Step 2: Generate all possible paths so far
        self.find_paths()


        # Step 3: Check if any of the generated paths are winning paths
        if self.check_for_winning_path():
            print("get_next_move: A winning path has been found!")
        else:
            print("get_next_move: No winning path yet.")

        print("")

        # Return the highest index as the next move, or None if no bridges are available
        return index


    def find_paths(self):
        # Get all red indexes from CellNodesFeatureList
        red_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Red"]
        print(f"find_paths: All the red indexes in CellNodeFeatureList are at: {red_indexes}")

        # Initialize red_edges_mapping to store edges for each red index
        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]
        self.Red_Paths = []

        # Populate red_edges_mapping with the edges for each red index
        for red_index in red_indexes:
            red_edges = self.all_edges[red_index]
            self.red_edges_mapping[red_index] = list(red_edges)

        # Debugging output to confirm structure
        print("\nfind_paths: Red indexes with their edges:")
        for index, edges in enumerate(self.red_edges_mapping):
            if edges:  # Print only non-empty entries for clarity
                print(f"find_paths: Index {index}: {edges}")

        # Check for paths between each pair of red nodes
        print("\nfind_paths: Paths between red nodes:")

        for i, red_index in enumerate(red_indexes):
            edges_for_index_i = set(self.red_edges_mapping[red_index])  # Convert to set for comparison
            print(f"\nfind_paths: Current Position being evaluated: {red_index} for Red")
            print(f"find_paths: Edges for red index {red_index}: {edges_for_index_i}")

            # Compare with subsequent red indexes
            for j in range( len(red_indexes)):
                next_red_index = red_indexes[j]
                edges_for_next_index = set(self.red_edges_mapping[next_red_index])

                # Find common edges
                common_edges = edges_for_index_i.intersection(edges_for_next_index)

                # Check if a bonded path exists due to direct adjacency (neighbors)
                if next_red_index in edges_for_index_i:
                    print(f"find_paths: Bonded path exists between red index {red_index} and red index {next_red_index} (neighbors).")
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


                if [next_red_index, red_index] not in self.Red_Paths and [red_index, next_red_index] not in self.Red_Paths:

                    # Check if there are at least two common edges
                    if len(common_edges) == 2:
                        print(
                            f"find_paths: Path exists between red index {red_index} and red index {next_red_index} with common edges: {common_edges}")
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
        print("\nfind_paths: Final Red paths with unique pairs:")
        print(self.Red_Paths)



    def check_for_winning_path(self):
        # Loop through each path in the RedPaths list
        for path in self.Red_Paths:
            touches_top_wall = False
            touches_bottom_wall = False

            # Check each index in the current path
            for index in path:
                # Check if index is near the top or bottom wall
                if index < self.board_size:
                    touches_top_wall = True
                elif index >= self.board_size * (self.board_size - 1):
                    touches_bottom_wall = True

                # If the path touches both top and bottom walls, it's a winning path
                if touches_top_wall and touches_bottom_wall:
                    print(f"check_for_winning_path: Winning path found: {path}")
                    break
            else:
                # If the loop completes without breaking, it's not a winning path
                print("check_for_winning_path: No winning path yet for this path:", path)

        return


    #check if the current position(index being evalueted) is touching the top or bot wall
    def check_top_bottom_wall(self, index):
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        if self.board_size is None:
            raise ValueError("check_top_bottom_wall: board_size must be set before calling check_top_bottom_wall.")

        if current_position < self.board_size:
            print(f"check_top_bottom_wall: Index {index} is touching the top wall.")
            return True
        elif current_position >= self.board_size * (self.board_size - 1):
            print(f"check_top_bottom_wall: Index {current_position} is touching the bottom wall.")
            return True
        return False


    def evaluate_bridge(self,  starting_index=None):
        current_position = starting_index if starting_index is not None else self.MoveList[-2]
        index = None
        print(f"evaluate_bridge: Evaluate bridge happening from starting index: {current_position}")

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":

                    # Distance of detected bp from current position
                    distances = [(x, abs(x - current_position)) for x in bridge_patterns]

                    # Find the longest distance from current position regardless of if its over or under the current
                    max_distance = max(distances, key=lambda x: x[1])[1]

                    # Get all bridge patterns that are at the maximum distance
                    farthest_patterns = [x[0] for x in distances if x[1] == max_distance]

                    # Prioritize selecting non-wall-adjacent farthest pattern if current_position already has a wall connection
                    selected_pattern = None
                    wall_touching = self.check_top_bottom_wall_NO_PRINT(current_position)

                    for pattern in farthest_patterns:
                        if wall_touching and not self.check_top_bottom_wall(pattern):
                            selected_pattern = pattern
                            print(f"evaluate_bridge: Selected non-wall-adjacent farthest index: {selected_pattern}")
                            break
                    else:
                        # If no non-wall option is found, default to random farthest pattern
                        selected_pattern = choice(farthest_patterns)
                        print(f"evaluate_bridge: Selected (default choice) farthest index: {selected_pattern}")

                    index = selected_pattern
                    print(f"evaluate_bridge: Red selected bridge pattern index: {index} from possible patterns {bridge_patterns}")

            if self.CellNodesFeatureList[current_position] == "Blue":
                print("-")
                """
                # Minimum distance to current_position
                min_distance = min(abs(x - current_position) for x in bridge_patterns)

                # Al bp that are minimum positions
                closest_patterns = [x for x in bridge_patterns if abs(x - current_position) == min_distance]

                # If multiple patterns are closest, pick one at random
                index = choice(closest_patterns)
                """

        # Recalculate paths to reflect the updated move
        self.find_paths_NO_PRINT()

        if self.check_for_winning_path():
            print("evaluate_bridge: A winning path has been found after updating paths with the new bridge index!")


        #When a possible brige pattern index has been used, remove from the PossibleBridgeList
        for sublist in self.PossibleBridgesList:
            if index in sublist:
                sublist.remove(index)
        print(f"evaluate_bridge: Removed {index} from all sublists in PossibleBridgesList,  ")

        return index









    def check_if_neigbour_is_with_wakll(self):
        index = None
        current_position = self.MoveList[-2]

        # Check if the current position itself is next to the wall
        if self.check_top_bottom_wall(current_position):
            print(f"check_if_neigbour_is_with_wakll: Current position {current_position} is next to a wall.")

            # Check if current_position is in an index in red path
            for path in self.Red_Paths:
                if current_position in path:
                    # Determine if current_position is the highest or lowest index in the path
                    if current_position == max(path):
                        current_position = min(path)  # Go to the lowest index in the path
                        print(f"check_if_neigbour_is_with_wakll: Current position {current_position} is the highest index in the path. Moving to new current position : {current_position}")

                    elif current_position == min(path):
                        current_position = max(path)  # Go to the highest index in the path
                        print(f"check_if_neigbour_is_with_wakll: Current position {current_position} is the lowest index in the path. Moving to new current position {current_position}")
                        # Instead of returning, use this index as a starting point for further bridge evaluation

                    # After updating, evaluate bridge for the new current_position
                    return self.evaluate_bridge(starting_index=current_position)

                # If no path is found, go directly to evaluating the bridge
            print("check_if_neigbour_is_with_wakll: No path found in Red_Paths for the current position. Going directly to evaluate bridge.")
            return self.evaluate_bridge()

        # Access the neighbors of the current position
        neighbours = self.all_edges[current_position]  # Use [] to index, not ()

        # Determine if the current position is part of a path that already has a top or bottom wall connection
        has_top_wall_touching = False
        has_bottom_wall_touching = False

        # Check the Red_Paths for wall touching nodes
        for path in self.Red_Paths:
            if current_position in path:
                # Check if any element in the path touches the top or bottom wall
                has_top_wall_touching = any(node < self.board_size for node in path)
                has_bottom_wall_touching = any(node >= self.board_size * (self.board_size - 1) for node in path)
                break


        # Collect neighbors that are touching the top or bottom wall
        wall_adjacent_neighbors = []
        for neighbor in neighbours:

            if neighbor < self.board_size:
                if not has_top_wall_touching:
                    print(f"check_if_neigbour_is_with_wakll: Neighbor {neighbor} is touching the top wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(f"check_if_neigbour_is_with_wakll: Neighbor {neighbor} is touching the top wall, but a top wall touching index already exists in the path. Skipping.")

            elif neighbor >= self.board_size * (self.board_size - 1):
                if not has_bottom_wall_touching:
                    print(f"check_if_neigbour_is_with_wakll: Neighbor {neighbor} is touching the bottom wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(f"check_if_neigbour_is_with_wakll: Neighbor {neighbor} is touching the bottom wall, but a bottom wall touching index already exists in the path. Skipping.")


        # Choose one of the wall-adjacent neighbors if available
        if wall_adjacent_neighbors:
            index = choice(wall_adjacent_neighbors)
            print(f"check_if_neigbour_is_with_wakll: Selected wall-adjacent neighbor: {index}")
            self.find_paths_NO_PRINT()

        if not wall_adjacent_neighbors:
            print(f"check_if_neigbour_is_with_wakll: No wall adjacent neighbors found, gonna do evaluate bridge")
            index = self.evaluate_bridge()

        return index










    def get_opposite_end_of_path_if_on_wall(self, current_position):
        # Check if the current position is next to the top or bottom wall
        if self.check_top_bottom_wall(current_position):
            print(f"get_opposite_end_of_path_if_on_wall: Index {current_position} is touching a wall. Checking paths in Red_Paths for {current_position}...")

            # Iterate over Red_Paths to find a path containing current_position
            for path in self.Red_Paths:
                print(f"get_opposite_end_of_path_if_on_wall: Checking path: {path}")
                if path and current_position in path:
                    # Determine the opposite end of the path
                    if current_position == path[0]:  # If current_position is at the start of the path
                        index = path[-1]  # Choose the last element
                        print(f"get_opposite_end_of_path_if_on_wall:  current_position is path[0]: Setting index to {index} from path {path}")
                    elif current_position == path[-1]:  # If current_position is at the end of the path
                        index = path[0]  # Choose the first element
                        print(f"get_opposite_end_of_path_if_on_wall:  current_position is path[-1]: Setting index to {index} from path {path}")

                    print(f"get_opposite_end_of_path_if_on_wall: Current position {current_position} is next to a wall. Opposite end index set to: {index}")
                    return index  # Return the opposite end index

            print(f"get_opposite_end_of_path_if_on_wall: No valid path found containing the current position {current_position} in Red_Paths.")

        return None  # Return None if no path found or not next to a wall


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
        if index >= board_size * 2 and index % self.board_size < ( self.board_size - 1):  # Ensure not in the first two rows and at least one position away from the right edge
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




        # Check if upper right bridge pattern is possible (as this seems likely relevant for 17)
        if index >= board_size and index % self.board_size < (self.board_size - 2):  # Ensure not in the first row and not in the first two positions from the right edge
 # Ensure not in the first row and at least one away from the right edge
            bp_top_right_index = (index - self.board_size + 2)
            up_l_index = (index - self.board_size + 1)
            up_r_index = (index + 1)

            if (0 <= bp_top_right_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_index < len(self.CellNodesFeatureList) and
                    0 <= up_r_index < len(self.CellNodesFeatureList)):

                if (self.CellNodesFeatureList[bp_top_right_index] == "None" and
                        self.CellNodesFeatureList[up_l_index] == "None" and
                        self.CellNodesFeatureList[up_r_index] == "None"):
                    self.PossibleBridgesList[index].append(bp_top_right_index)


        # Check if the upper left bridge pattern is possible
        if index >= board_size and index % self.board_size > 0:  # Ensure not in the first row and at least one position away from the left edge
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
        if index < board_size * (board_size - 2) and index % self.board_size > 0:  # Ensure not in the last two rows and at least one position away from the left edge
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
        if index < board_size * (board_size - 1) and index % self.board_size < (self.board_size - 1):  # Ensure not in the last row and at least one position away from the right edge
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
        if index < board_size * (board_size - 1) and index % self.board_size > 1:  # Ensure not in the last row and at least two positions away from the left edge
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






    def find_paths_NO_PRINT(self):
        # Get all red indexes from CellNodesFeatureList
        red_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Red"]

        # Initialize red_edges_mapping to store edges for each red index
        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]
        self.Red_Paths = []

        # Populate red_edges_mapping with the edges for each red index
        for red_index in red_indexes:
            red_edges = self.all_edges[red_index]
            self.red_edges_mapping[red_index] = list(red_edges)


        for i, red_index in enumerate(red_indexes):
            edges_for_index_i = set(self.red_edges_mapping[red_index])  # Convert to set for comparison

            # Compare with subsequent red indexes
            for j in range( len(red_indexes)):
                next_red_index = red_indexes[j]
                edges_for_next_index = set(self.red_edges_mapping[next_red_index])

                # Find common edges
                common_edges = edges_for_index_i.intersection(edges_for_next_index)

                # Check if a bonded path exists due to direct adjacency (neighbors)
                if next_red_index in edges_for_index_i:
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

                if [next_red_index, red_index] not in self.Red_Paths and [red_index, next_red_index] not in self.Red_Paths:

                    # Check if there are at least two common edges
                    if len(common_edges) == 2:
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



    def check_for_winning_path_NO_PRINT(self):
        # Loop through each path in the RedPaths list
        for path in self.Red_Paths:
            touches_top_wall = False
            touches_bottom_wall = False

            # Check each index in the current path
            for index in path:
                # Check if index is near the top or bottom wall
                if index < self.board_size:
                    touches_top_wall = True
                elif index >= self.board_size * (self.board_size - 1):
                    touches_bottom_wall = True

                # If the path touches both top and bottom walls, it's a winning path
                if touches_top_wall and touches_bottom_wall:
                    break

        return




    #check if the current position(index being evalueted) is touching the top or bot wall
    def check_top_bottom_wall_NO_PRINT(self, index):
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        if current_position < self.board_size:
            return True
        elif current_position >= self.board_size * (self.board_size - 1):
            return True
        return False














