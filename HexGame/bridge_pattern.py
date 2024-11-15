from random import choice

from jinja2.nodes import Break
from numba.cuda import detect


class BP:

    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list,  current_winning_path, red_path, move_list, All_Edges,  RedAI, BlueAI, red_bp):
        self.board_size = size
        self.Player1 = True
        self.Winner = None
        self.redAI = RedAI
        self.blueAI = BlueAI
        self.not_previous_disruption = True

        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = cell_node_feature_list

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell with the same symbol
        self.CellNodesEdgeList = cell_nodes_edge_list

        # A single array in this list of arrays represents a path for player red
        self.RedPaths = red_path


        # Array that contains a moves done
        self.MoveList = move_list

        self.all_edges = All_Edges

        # Array that contains the possible bridges
        self.PossibleBridgesList = [[] for _ in range(self.board_size * self.board_size)]

        self.Red_Bp = red_bp

        self.Blue_Bp = [[] for _ in range(self.board_size * self.board_size)]

        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]

        self.Current_Winning_Path = current_winning_path

        return



    def get_next_move(self):
        index = None
        paths = None

        if len(self.MoveList) < 2:
            print("\nget_next_move: Both players need to make at least one move")
            return None

        current_position = self.MoveList[-2]

        playerColor = self.CellNodesFeatureList[current_position]

        print(f"get_next_move: Current Position being evaluated: {current_position} for {playerColor} ")

        if playerColor == "Red":
            if self.redAI:
                print("get_next_move: Red is using AI")
                index = self.get_next_move_with_AI()
            else:
                print("get_next_move: Red is not using AI")

        if playerColor == "Blue":
            if self.blueAI:
                print("get_next_move: Blue is using AI")
                index = self.get_next_move_with_AI()
            else:
                print("get_next_move: Blue is not using AI")
        return index


    def get_next_move_with_AI(self):
        index = None

        current_position = self.MoveList[-2]

        # Step 1: Set the starting position based on whether a disruption occurred
        if self.not_previous_disruption:
            # Go back 4 moves if there was a previous disruption
            current_position = self.MoveList[-2]
            print(f"get_next_move_with_AI: Adjusting position due to disruption, current_position set to {current_position}")
            self.not_previous_disruption = True
        else:
            # Default to the last move if no disruption
            current_position = self.MoveList[-4]
            print(f"get_next_move_with_AI: No disruption, current_position set to {current_position}")

        playerColor = self.CellNodesFeatureList[current_position]
        print(f"get_next_move_with_AI: Current position {current_position} before detect paths")

        # Step A: Detect paths
        self.detect_paths()
        print(f"get_next_move_with_AI: Detected paths, current RedPaths: {self.RedPaths}")

        # Step B: Check for path disruption
        path_disruption = self.disrupted_paths()
        print(f"get_next_move_with_AI: path_disruption returned: {path_disruption}")

        # Step C: Handle path disruption if detected
        if path_disruption is not None:
            print(f"get_next_move_with_AI: Path {self.RedPaths} has been disrupted at {path_disruption}")
            self.previous_disruption = True
            # Go back 4 moves in the next call if a disruption occurs
            return path_disruption
        else:
            self.previous_disruption = False
            print("get_next_move_with_AI: No path disruption detected.")

        path_disruption = self.disrupted_paths()
        # Step B: If the current winning path has any disruption, fix it  (I NEED TO DETERMINE CURRENT WINNING PATH)
        if path_disruption is not None:
            print(f"get_next_move_with_AI: The path {self.RedPaths} has in fact been disrupted")
            self.previous_disruption = True
            return path_disruption
        else:
            self.previous_disruption = False


        print(f"get_next_move_with_AI: {current_position} after path_disruption and before winning path ")

        self.winning_path()

        """
        filled_bp_index = self.winning_path()

        if filled_bp_index is not None:
            print(f"get_next_move_with_AI: The current winning {self.current_winning_path} has an index filled at {filled_bp_index}")
            return filled_bp_index
        """
        #Step C



        # Step C: If the current path touches a top or bottom, pick the current position on the opposite side to fully connect






        #current_position = self.current_winning_path[-1] if self.current_winning_path else self.MoveList[-2]
        new_position = self.switch_position_on_wall_contact(current_position)
        if new_position != current_position:
            print(f"get_next_move_with_AI: Updated current position from {current_position} to {new_position} after wall contact.")
            current_position = new_position

        print(f"get_next_move_with_AI: Current position before step 1 : {current_position}")

        path_touching_wall = False  # Flag to check if the path touches a wall

        if playerColor == "Red":

            # Step 1: If current position is touching a wall go to detect and evaluate bridge:
            if current_position < self.board_size:
                print(f"get_next_move_with_AI STEP 1: Current Position {current_position} for red is next to top wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index

            if current_position >= self.board_size * (self.board_size - 1):
                print(f"get_next_move_with_AI: STEP 1: Current Position {current_position} for red is next to bottom wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index

        if playerColor == "Blue":
            if current_position % self.board_size == 0:
                print(f"get_next_move_with_AI: STEP 1: Current Position {current_position} for blue is next to left wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index
            if current_position % self.board_size == self.board_size - 1:
                print(f"get_next_move_with_AI: STEP 1: Current Position {current_position} for blue is next to right wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index



        print(f"Current position before step 2 : {current_position}")
        print(f"get_next_move_with_AI: Current position before step 2 : {current_position}")




        # Step 2: If a wall-adjacent neighbor is detected, return that neighbor as Index
        neighbor_with_wall = self.detect_neighbours_is_with_wall(current_position)
        print(f"get_next_move_with_AI: STEP 2: Detected wall-adjacent neighbor: {neighbor_with_wall}")

        if neighbor_with_wall is not None and neighbor_with_wall not in self.MoveList:
            print(f"get_next_move_with_AI: STEP 2: Returning wall-adjacent neighbor {neighbor_with_wall} as the next move")
            return neighbor_with_wall  # End the function here if a wall-adjacent neighbor is found

        print("get_next_move_with_AI: STEP 2/3:  No wall-adjacent neighbors detected, proceeding to bridge detection")



        # Step 3: Check if current position has detected bridges , if so evaluate them
        self.detect_bridge(current_position)
        possible_bridges = self.PossibleBridgesList[current_position]

        if possible_bridges:  # Checks if possible_bridges is non-empty
            print(f"get_next_move_with_AI: STEP 3:  All possible bridges detected in {current_position} are: {possible_bridges}, will now evaluate them to pick the best one.")
            index = self.evaluate_bridge(current_position)
            return index
        else:
            print("get_next_move_with_AI: STEP 3:  no bridgesfound , retuning index as none")

            index = None

        return index


    def detect_paths(self):
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        if playerColor == "Red":
            # Get all red indexes from CellNodesFeatureList
            red_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Red"]
            print(f"detect_paths: All the red indexes in CellNodeFeatureList are at: {red_indexes}")


            # For loop going through all red indexes and getting their edges
            for red_index in red_indexes:
                red_edges = self.all_edges[red_index]
                self.red_edges_mapping[red_index] = list(red_edges)

            # Prints out all the red indexes with their corresponding edges from the list red_edges_mapping
            print("\ndetect_paths: Red indexes with their edges:")
            for index, edges in enumerate(self.red_edges_mapping):
                if edges:  # Only print non-empty entries for clarity
                    print(f"detect_paths: Index {index}: {edges}")



            # Check for paths between each pair of red nodes
            print("\ndetect_paths: Paths between red nodes:")


            for i, red_index in enumerate(red_indexes):
                edges_for_index_i = set(self.red_edges_mapping[red_index])
                print(f"\ndetect_paths: Current Position being evaluated: {red_index} for Red")
                print(f"detect_paths: Edges for red index {red_index}: {edges_for_index_i}")

                # Compare with subsequent red indexes to check for paths
                for j in range(i + 1, len(red_indexes)):
                    next_red_index = red_indexes[j]
                    edges_for_next_index = set(self.red_edges_mapping[next_red_index])

                    # Find common edges between red_index and next_red_index
                    common_edges = edges_for_index_i.intersection(edges_for_next_index)

                    # Handle direct adjacency connection (neighboring nodes)
                    if next_red_index in edges_for_index_i:
                        print(f"detect_paths: Bonded path exists between red index {red_index} and red index {next_red_index} (neighbors).")
                        path_found = False

                        # Search for existing path that includes red_index or next_red_index
                        for path in self.RedPaths:
                            if red_index in path or next_red_index in path:
                                # Extend the existing path with any new unique nodes
                                if red_index not in path:
                                    path.append(red_index)
                                if next_red_index not in path:
                                    path.append(next_red_index)
                                path_found = True
                                print(f"detect_paths: Added {red_index} and {next_red_index} to existing path: {path}")
                                break

                        # If no path was found, create a new separate path for these connected nodes
                        if not path_found:
                            self.RedPaths.append([red_index, next_red_index])
                            print(f"detect_paths: Created new path: [{red_index}, {next_red_index}]")



                    # Handle bridge pattern connection (two common edges)
                    if len(common_edges) == 2:
                        print( f"detect_paths: Path exists between red index {red_index} and red index {next_red_index} with common edges: {common_edges}")
                        path_found = False

                        # Search for an existing path that includes red_index or next_red_index
                        for path in self.RedPaths:
                            if red_index in path or next_red_index in path:
                                # Extend the existing path with any new unique nodes
                                if red_index not in path:
                                    path.append(red_index)
                                if next_red_index not in path:
                                    path.append(next_red_index)
                                path_found = True
                                break

                        # If no path was found, create a new separate path for these nodes
                        if not path_found:
                            self.RedPaths.append([red_index, next_red_index])
                            print(f"detect_paths: Created new path: [{red_index}, {next_red_index}]")



            # Step: Find the path with the longest top-to-bottom coverage
            longest_path = None
            max_coverage = 0
            self.Current_Winning_Path = []

            for path in self.RedPaths:
                if path:
                    min_index = min(path)
                    max_index = max(path)
                    coverage = max_index - min_index

                    print(f"detect_paths: Evaluating path {path}: min index = {min_index}, max index = {max_index}, coverage = {coverage}")

                    # Update if this path has the longest coverage seen so far
                    if coverage > max_coverage:
                        max_coverage = coverage
                        longest_path = path

            # Print the path with the longest top-to-bottom coverage
            if longest_path is not None:
                self.Current_Winning_Path = longest_path
                print(f"\ndetect_paths: The path with the longest top-to-bottom coverage is: {longest_path} with coverage of {max_coverage}")
            else:
                print("\ndetect_paths: No valid paths found.")
                self.Current_Winning_Path = []



            # Final output of all unique paths
            print("\ndetect_paths: Final Red paths with unique pairs:")
            print(self.RedPaths)



    def winning_path(self):
        # Check if any position in current_winning_path touches the top wall
        touching_top_wall = any(pos < self.board_size for pos in self.Current_Winning_Path)

        # Check if any position in current_winning_path touches the bottom wall
        touching_bottom_wall = any(pos >= self.board_size * (self.board_size - 1) for pos in self.Current_Winning_Path)

        # Combined condition to check if the path touches both the top and bottom walls
        if touching_top_wall and touching_bottom_wall:
            print(f"current_winning_path {self.Current_Winning_Path} is touching both the top and bottom walls.")

            # Confirm that the path is fully connected in a bridge pattern
            fully_connected = True
            for i in range(len(self.Current_Winning_Path) - 1):
                node_a = self.Current_Winning_Path[i]
                node_b = self.Current_Winning_Path[i + 1]

                # Find shared edges (bridge connections) between node_a and node_b
                neighbors_a = set(self.red_edges_mapping[node_a])
                neighbors_b = set(self.red_edges_mapping[node_b])
                shared_edges = neighbors_a.intersection(neighbors_b)
                shared_edges_list = list(shared_edges)

                print(f"winning_path: shared_edges_list: {shared_edges_list}")

                # Check if there are at least two shared edges to form a valid bridge
                if len(shared_edges_list) < 2:
                    print("winning_path: Not enough shared edges to form a bridge pattern.")
                    fully_connected = False
                    break

                # Confirm mutual connection in the all_edges map
                if (shared_edges_list[0] not in self.all_edges[shared_edges_list[1]] or
                        shared_edges_list[1] not in self.all_edges[shared_edges_list[0]]):
                    print("winning_path: This is not a bridge pattern; disruption detected.")
                    fully_connected = False
                    break

            # If fully connected, then proceed to fill
            if fully_connected:
                for i in range(len(self.Current_Winning_Path) - 1):
                    node_a = self.Current_Winning_Path[i]
                    node_b = self.Current_Winning_Path[i + 1]
                    neighbors_a = set(self.red_edges_mapping[node_a])
                    neighbors_b = set(self.red_edges_mapping[node_b])
                    shared_edges = neighbors_a.intersection(neighbors_b)
                    shared_edges_list = list(shared_edges)

                    if (self.CellNodesFeatureList[shared_edges_list[0]] == "None" and
                            self.CellNodesFeatureList[shared_edges_list[1]] == "None"):
                        fill_bp_index = choice(shared_edges_list)
                        print(f"winning_path: Filled edge {fill_bp_index} between nodes {node_a} and {node_b}.")
                        return fill_bp_index

        return None




    def disrupted_paths(self):
        current_player_color = "Blue"

        if self.Player1:
            current_player_color = "Red"
        else:
            current_player_color = "Blue"

        for path_index, path in enumerate(self.RedPaths):  # Use enumerate to get both index and path
            # Go through each pair of nodes in the path to check their shared edges
            for i in range(len(path) - 1):
                node_a = path[i]
                node_b = path[i + 1]

                # Find the common edges (neighbors) between node_a and node_b
                neighbors_a = set(self.red_edges_mapping[node_a])
                neighbors_b = set(self.red_edges_mapping[node_b])
                shared_edges = neighbors_a.intersection(neighbors_b)
                shared_edges_list = list(shared_edges)

                # Initialize variables to track the status of shared edges
                occupied_by_opponent = None  # Index of a cell occupied by opponent
                occupied_by_self = False  # Flag to indicate if any cell is occupied by the current player
                unoccupied_index = None  # Index of an unoccupied cell


                print(f"disrupted_paths: Shared edges list: {shared_edges_list}")
                print(f"disrupted_paths: Self.all_edges[[shared_edges_list[0]]]: {self.all_edges[shared_edges_list[0]]}")
                print(f"disrupted_paths: Self.all_edges[[shared_edges_list[1]]]: {self.all_edges[shared_edges_list[1]]}")


                # If the first index in shared_edges_list is an edge for second shared_edges_list index
                if shared_edges_list[0] not in self.all_edges[shared_edges_list[1]]:
                    print("disrupted_paths: This is not a bridge pattern the disruption is happening at1")
                    return None

                # If the first second in shared_edges_list is an edge for first shared_edges_list index
                if shared_edges_list[1] not in self.all_edges[shared_edges_list[0]]:
                    print("disrupted_paths: This is not a bridge pattern the disruption is happening at2")
                    return None

                # Assuming `current_player_color` holds the current player's color (e.g., "Red" or "Blue")
                for edge in shared_edges_list:
                    cell_status = self.CellNodesFeatureList[edge]
                    cell_status = self.CellNodesFeatureList[edge]

                    if cell_status == "None":
                        unoccupied_index = edge  # Track an unoccupied cell index
                    elif cell_status == current_player_color:
                        occupied_by_self = True  # Mark that a cell is occupied by the current player
                    else:
                        occupied_by_opponent = edge  # Track opponent's occupied cell

                # Determine the outcome based on occupancy status
                if occupied_by_self:
                    # Return False if any shared edge cell is occupied by the current player's piece
                    print("disrupted_paths: One of the cells is occupied by the current player's piece.")
                    return None
                elif occupied_by_opponent is not None and unoccupied_index is not None:
                    # Return the unoccupied cell index if only one cell is occupied by the opponent
                    print(f"disrupted_paths: Returning unoccupied cell index {unoccupied_index}.")
                    return unoccupied_index
                elif occupied_by_opponent is not None and unoccupied_index is None:
                    # Both cells are occupied (by opponent or otherwise), return None
                    print("disrupted_paths: Both shared edge cells are occupied. Returning None.")
                    return None
                else:
                    # No specific conditions met; return None as a default
                    print("disrupted_paths: No conditions met. Returning None.")
                    return None







    def switch_position_on_wall_contact(self, current_position):
        # Check if the current position itself is next to a wall
        if current_position < self.board_size or current_position >= self.board_size * (self.board_size - 1):
            print(f"switch_position_on_wall_contact: Current position {current_position} is next to a wall.")

            # Check if current_position is part of any path in RedPaths
            for path in self.RedPaths:
                if current_position in path:
                    unique_path_elements = list(set(path))
                    print(
                        f"switch_position_on_wall_contact: Unique elements in the path containing {current_position} are {unique_path_elements}")

                    if len(unique_path_elements) > 1:
                        # Check if current_position is the highest in the path (bottom wall contact), then move to the lowest
                        if current_position == max(unique_path_elements):
                            new_position = min(unique_path_elements)
                            print(
                                f"switch_position_on_wall_contact: Current position {current_position} is the highest index in the path (touching bottom wall). Moving to new current position: {new_position}")
                            return new_position

                        # Check if current_position is the lowest in the path (top wall contact), then move to the highest
                        elif current_position == min(unique_path_elements):
                            new_position = max(unique_path_elements)
                            print(
                                f"switch_position_on_wall_contact: Current position {current_position} is the lowest index in the path (touching top wall). Moving to new current position: {new_position}")
                            return new_position

                    else:
                        # If the current position is the only unique element in the path or isn't in a path
                        print(
                            f"switch_position_on_wall_contact: Current position {current_position} is the only unique element in the path or isn't in a path, so no movement is needed.")
                # No `break` here to ensure all paths are checked

            # Access the neighbors of the current position

        neighbours = self.all_edges[current_position]  # Use [] to index, not ()

        # Determine if the current position is part of a path that already has a top or bottom wall connection
        has_top_wall_touching = False
        has_bottom_wall_touching = False

        # Check the Red_Paths for wall touching nodes
        for path in self.RedPaths:
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
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the top wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the top wall, but a top wall touching index already exists in the path. Skipping.")

            elif neighbor >= self.board_size * (self.board_size - 1):
                if not has_bottom_wall_touching:
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the bottom wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the bottom wall, but a bottom wall touching index already exists in the path. Skipping.")

        return current_position  # Return current position if no wall contact switch is needed


    #checks if any neigbours of the current position are touching the top or bottom wall
    def detect_neighbours_is_with_wall(self, current_position):
        index = None
        neighbours = self.all_edges[current_position]
        playerColor = self.CellNodesFeatureList[current_position]

        wall_adjacent_neighbors = []

        # Check if current_position is part of a path that already touches the top wall
        #        if playerColor == "Red" and hasattr(self, 'current_winning_path'):
        if playerColor == "Red":
            in_top_wall_path = any(pos < self.board_size for pos in self.Current_Winning_Path if current_position in self.Current_Winning_Path)
            in_bot_wall_path = any(pos >= self.board_size * (self.board_size - 1) for pos in self.Current_Winning_Path if current_position in self.Current_Winning_Path)

            if in_top_wall_path:
                print(
                    f"detect_neighbours_is_with_wall: Current position {current_position} is in a path that already touches the top wall. Skipping wall-adjacent neighbors.")
                return None  # Skip adding wall-adjacent neighbors if already touching the top wall


            if in_bot_wall_path:
                print(
                    f"detect_neighbours_is_with_wall: Current position {current_position} is in a path that already touches the top wall. Skipping wall-adjacent neighbors.")
                return None  # Skip adding wall-adjacent neighbors if already touching the top wall
        if playerColor == "Red":
            for neighbor in neighbours:
                #if neighbours are touching the top wall , append those neighbours indexes in wall_adjacent_neighbours
                if neighbor < self.board_size and self.CellNodesFeatureList[neighbor] == "None":
                        print(f"check_if_neighbours_is_with_wall: Neighbor {neighbor} is touching the top wall.")
                        wall_adjacent_neighbors.append(neighbor)

                #if neighbours are touching the bottom wall, append those neighbours indexes in wall_adjacent_neighbours
                elif neighbor >= self.board_size * (self.board_size - 1) and self.CellNodesFeatureList[neighbor] == "None":
                        print(f"check_if_neighbours_is_with_wall: Neighbor {neighbor} is touching the bottom wall.")
                        wall_adjacent_neighbors.append(neighbor)


        if playerColor == "Blue":
            for neighbours in neighbours:
                # if neighbours are touching the left wall, append those neighbours indexes in wall_adjacent_neighbours
                if neighbours % self.board_size == 0:
                    print(f"check_if_neighbours_is_with_wall: Neighbor {neighbours} is touching the left wall.")
                    wall_adjacent_neighbors.append(neighbours)

                # if neighbours are touching the right wall, append those neighbours indexes in wall_adjacent_neighbours
                elif neighbours % self.board_size == self.board_size - 1:
                    print(f"check_if_neighbours_is_with_wall: Neighbor {neighbours} is touching the right wall.")
                    wall_adjacent_neighbors.append(neighbours)

        #if there are neighbours that are wall-adjacent, chose them as an index, if there are multiple, pick one of them
        if wall_adjacent_neighbors:
            index = choice(wall_adjacent_neighbors)
            print(f"check_if_neighbours_is_with_wall: Selected wall-adjacent neighbor: {index}")
        else:
            print(f"check_if_neighbours_is_with_wall: No wall adjacent neighbors found, gonna do evaluate bridge")

        return index







    def detect_neighbours_is_with_wall_NO_PRINT(self, current_position):
        index = None
        current_position = self.MoveList[-2]
        neighbours = self.all_edges[current_position]
        wall_adjacent_neighbors = []

        for neighbor in neighbours:
            #if neigbours are touching the top wall wall wall, append those neigbours indexes in wall_adjacent_neigbour
            if neighbor < self.board_size:
                    wall_adjacent_neighbors.append(neighbor)
            #if neigbours are touching the bottom wall wall wall, append those neigbours indexes in wall_adjacent_neigbour
            elif neighbor >= self.board_size * (self.board_size - 1):
                    wall_adjacent_neighbors.append(neighbor)

        #if there are neigbours that are wall-adjacent, chose them as an index, if there are multiple, pick one of them
        if wall_adjacent_neighbors:
            index = choice(wall_adjacent_neighbors)

        return index



    #detects bridges for current position
    def detect_bridge(self, index):
        playerColor = self.CellNodesFeatureList[index]
        board_size = self.board_size
        self.PossibleBridgesList[index].clear()
        print(f"detect_bridge: Evaluating bridge patterns for index {index} with color {playerColor}")

        # Check if the most upper bridge pattern is possible
        if index >= board_size * 2 and index % self.board_size < (self.board_size - 1):
            bp_top_index = (index - 2 * board_size + 1)
            top_r_index = (index - board_size + 1)
            top_l_index = (index - board_size)
            if 0 <= bp_top_index < len(self.CellNodesFeatureList) and 0 <= top_r_index < len(self.CellNodesFeatureList) and 0 <= top_l_index < len(self.CellNodesFeatureList) and index % board_size != board_size - 1:  # Ensure index is not on the right edge
                if self.CellNodesFeatureList[bp_top_index] == "None" and self.CellNodesFeatureList[top_r_index] == "None" and self.CellNodesFeatureList[top_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_index)

        # Check if upper right bridge pattern is possible
        if index >= board_size and index % self.board_size < (self.board_size - 2):
            bp_top_right_index = (index - self.board_size + 2)
            up_l_index = (index - self.board_size + 1)
            up_r_index = (index + 1)
            if 0 <= bp_top_right_index < len(self.CellNodesFeatureList) and 0 <= up_l_index < len(self.CellNodesFeatureList) and 0 <= up_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_right_index] == "None" and self.CellNodesFeatureList[up_l_index] == "None" and self.CellNodesFeatureList[up_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_right_index)

        # Check if the upper left bridge pattern is possible
        if index >= board_size and index % self.board_size > 0:
            bp_top_left_index = (index - board_size - 1)
            up_l_up_index = (index - board_size)
            up_l_down_index = (index - 1)
            if 0 <= bp_top_left_index < len(self.CellNodesFeatureList) and 0 <= up_l_up_index < len(self.CellNodesFeatureList) and 0 <= up_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_left_index] == "None" and self.CellNodesFeatureList[up_l_up_index] == "None" and self.CellNodesFeatureList[up_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_left_index)

        # Check if most down bridge pattern is possible
        if index < board_size * (board_size - 2) and index % self.board_size > 0:  # Ensure not in the last two rows and at least one position away from the left edge
            bp_bot_index = (index + 2 * self.board_size - 1)
            bot_r_index = (index + self.board_size - 1)
            bot_l_index = (index + self.board_size)
            if (0 <= bp_bot_index < len(self.CellNodesFeatureList) and 0 <= bot_r_index < len(self.CellNodesFeatureList) and 0 <= bot_l_index < len(self.CellNodesFeatureList) and index % self.board_size != (self.board_size + 2)):
                if self.CellNodesFeatureList[bp_bot_index] == "None" and self.CellNodesFeatureList[bot_r_index] == "None" and self.CellNodesFeatureList[bot_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_index)

        # Check if the bottom right bridge pattern is possible
        if index < board_size * (board_size - 1) and index % self.board_size < (self.board_size - 1):  # Ensure not in the last row and at least one position away from the right edge
            bp_bot_right_index = (index + board_size + 1)
            bot_l_index = (index + board_size)
            bot_r_index = (index + 1)
            if 0 <= bp_bot_right_index < len(self.CellNodesFeatureList) and 0 <= bot_l_index < len(self.CellNodesFeatureList) and 0 <= bot_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_right_index] == "None" and self.CellNodesFeatureList[bot_l_index] == "None" and self.CellNodesFeatureList[bot_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_right_index)

        # Check if the bottom left bridge pattern is possible
        if index < board_size * (board_size - 1) and index % self.board_size > 1:  # Ensure not in the last row and at least two positions away from the left edge
            bp_bot_left_index = (index + board_size - 2)
            bot_l_down_index = (index + board_size - 1)
            bot_l_up_index = (index - 1)
            if 0 <= bp_bot_left_index < len(self.CellNodesFeatureList) and 0 <= bot_l_up_index < len(self.CellNodesFeatureList) and 0 <= bot_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_left_index] == "None" and self.CellNodesFeatureList[bot_l_up_index] == "None" and  self.CellNodesFeatureList[bot_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_left_index)



    def evaluate_bridge(self, current_position):
        selected_pattern = None

        print(f"evaluate_bridge: Evaluate bridge happening from starting index: {current_position}")

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        if not bridge_patterns:
            print(f"evaluate_bridge: No bridge patterns found in PossibleBridgesList")

        # Determine if current_position is part of the winning path and if that path touches the top wall
        in_winning_path = current_position in self.Current_Winning_Path if hasattr(self, 'current_winning_path') else False
        path_touches_top_wall = any(pos < self.board_size for pos in self.Current_Winning_Path) if in_winning_path else False
        path_touches_bottom_wall = any(pos >= self.board_size * (self.board_size - 1) for pos in self.Current_Winning_Path) if in_winning_path else False

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":
                print(f"Evaluate bridge happening from {self.CellNodesFeatureList[current_position]}")

                # Filter out bridge patterns that would lead to top wall positions if the path touches the top wall
                if path_touches_top_wall:
                    print(f"evaluate_bridge: hei Path containing {current_position} touches the top wall. Filtering out bridges to top wall positions.")
                    bridge_patterns = [pos for pos in bridge_patterns if pos >= self.board_size]

                    # Sort bridge patterns in descending order (highest indexes first) to prioritize downward movement
                    sorted_patterns = sorted(bridge_patterns, reverse=True)
                    selected_pattern = sorted_patterns[0] if sorted_patterns else None
                    self.Red_Bp.append(selected_pattern)
                    print(f"evaluate_bridge: hei Selected highest index pattern: {selected_pattern} from possible patterns {sorted_patterns}")

                # Prioritize lowest bridge pattern for upward movement if path touches the bottom wall
                elif path_touches_bottom_wall:
                    print(f"evaluate_bridge: hei Path containing {current_position} touches the bottom wall. Prioritizing the lowest bridge pattern for upward movement.")
                    selected_pattern = min(bridge_patterns)  # Choose the bridge pattern with the lowest index
                    print(f"evaluate_bridge: hei Selected lowest index pattern: {selected_pattern} from possible patterns {bridge_patterns}")
                    self.Red_Bp.append(selected_pattern)


                else:
                    # Distance of detected bp from current position
                    distances = [(x, abs(x - current_position)) for x in bridge_patterns]
                    # Find the longest distance from current position regardless of if its over or under the current
                    max_distance = max(distances, key=lambda x: x[1])[1]
                    # Get all bridge patterns that are at the maximum distance
                    farthest_patterns = [x[0] for x in distances if x[1] == max_distance]


                    #Goes through list of bridge patterns in current position and does an if check
                    # If a bp index touching a top or bottom wall, choose that as the index
                    for pattern in bridge_patterns:
                        # Check if the pattern is wall-adjacent based on downward movement preference
                        if  pattern < self.board_size:
                            selected_pattern = pattern
                            self.Red_Bp.append(selected_pattern)

                            print(f"evaluate_bridge: Selected top-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break
                        if  pattern >= self.board_size * (self.board_size - 1):
                            selected_pattern = pattern
                            self.Red_Bp.append(selected_pattern)
                            print(f"evaluate_bridge: Selected bottom-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break

                    # Default to a random farthest pattern if no suitable pattern is found
                    if selected_pattern is None and farthest_patterns:
                        selected_pattern = choice(farthest_patterns)
                        self.Red_Bp.append(selected_pattern)
                        print(f"evaluate_bridge: Selected farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                    print(f"evaluate_bridge: Red selected bridge pattern index: {selected_pattern} from possible patterns {bridge_patterns}")




            if self.CellNodesFeatureList[current_position] == "Blue":
                print(f"Evaluate bridge happening from {self.CellNodesFeatureList[current_position]}")

                # Distance of detected bridge patterns (bp) from the current position
                distances = [(x, abs(x - current_position)) for x in bridge_patterns]

                # Find the shortest distance from current position
                min_distance = min(distances, key=lambda x: x[1])[1]

                # Get all bridge patterns that are at the minimum distance
                closest_patterns = [x[0] for x in distances if x[1] == min_distance]

                # Goes through list of bridge patterns in current position and does an if check
                # If a bp index touching a top or bottom wall, choose that as the index
                for pattern in bridge_patterns:
                    if isinstance(pattern, int):
                        if pattern % self.board_size == 0:
                            selected_pattern = pattern
                            print(f"evaluate_bridge: Selected left-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break
                        if pattern % self.board_size == self.board_size - 1:
                            selected_pattern = pattern
                            print(f"evaluate_bridge: Selected right-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break

                # Default to a random farthest pattern if no suitable pattern is found
                if selected_pattern is None:
                    selected_pattern = choice(closest_patterns)
                    print(
                        f"evaluate_bridge: Selected closest index: {selected_pattern} from possible patterns {bridge_patterns}")
                print(
                    f"evaluate_bridge: Blue selected bridge pattern index: {selected_pattern} from possible patterns {bridge_patterns}")

            # When a possible bridge pattern index has been used, remove from the PossibleBridgeList
            for sublist in self.PossibleBridgesList:
                if selected_pattern in sublist:
                    sublist.remove(selected_pattern)
            print(f"evaluate_bridge: Removed {selected_pattern} from all sublists in PossibleBridgesList")



        return selected_pattern




    #check if the current position(index being evalueted) is touching the top or bot wall
    def check_top_bottom_wall_NO_PRINT(self, index):
        current_position = self.MoveList[-2]

        if current_position < self.board_size:
            return True
        elif current_position >= self.board_size * (self.board_size - 1):
            return True
        return False




























