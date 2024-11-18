from random import choice


class BP:

    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list, current_winning_path, red_path, move_list,
                 All_Edges, RedAI, BlueAI, red_bp, blue_bp, blue_path):
        self.board_size = size
        self.Player1 = True
        self.Winner = None
        self.redAI = RedAI
        self.blueAI = BlueAI
        self.previous_disruption = False

        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = cell_node_feature_list

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell with the same symbol
        self.CellNodesEdgeList = cell_nodes_edge_list

        # A single array in this list of arrays represents a path for player red
        self.RedPaths = red_path

        self.BluePaths = blue_path

        # Array that contains a moves done
        self.MoveList = move_list

        self.all_edges = All_Edges

        # Array that contains the possible bridges
        self.PossibleBridgesList = [[] for _ in range(self.board_size * self.board_size)]

        self.Red_Bp = red_bp
        
        self.Blue_Bp = blue_bp

        self.red_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]


        self.blue_edges_mapping = [[] for _ in range(self.board_size * self.board_size)]


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

        ################
        # Detect Paths #
        ################
        self.detect_paths()
        print(f"get_next_move_with_AI: Detected paths, current RedPaths: {self.RedPaths}")

        #################################################
        # Check if disruption has occured previous move #
        #################################################
        if self.previous_disruption:
            # Go back 4 moves if there was a previous disruption
            current_position = self.MoveList[-4]
            print(
                f"get_next_move_with_AI: Adjusting position due to disruption, current_position set to {current_position}")
            self.previous_disruption = True
        else:
            # Default to the last move if no disruption
            current_position = self.MoveList[-2]
            print(f"get_next_move_with_AI: No disruption, current_position set to {current_position}")
        playerColor = self.CellNodesFeatureList[current_position]
        print(f"get_next_move_with_AI: Current position {current_position} before detect paths")

        ###################################
        # Check if disruption has occured #
        ###################################
        path_disruption = self.disrupted_paths()
        print(f"get_next_move_with_AI: path_disruption returned: {path_disruption}")
        if path_disruption is not None:
            print(f"get_next_move_with_AI: Path {self.RedPaths} has been disrupted at {path_disruption}")
            self.previous_disruption = True
            # Go back 4 moves in the next call if a disruption occurs
            return path_disruption
        else:
            self.previous_disruption = False
            print("get_next_move_with_AI: No path disruption detected.")
        print(f"get_next_move_with_AI: {current_position} after path_disruption and before winning path ")

        ############################################################
        # If winning path has been detected begin filling the gaps #
        ############################################################
        filled_bp_index = self.winning_path()
        if filled_bp_index is not None:
            print(
                f"get_next_move_with_AI: The current winning {self.Current_Winning_Path} has an index filled at {filled_bp_index}")
            return filled_bp_index

        #################################################################
        # If was has been touched switch a non-touched wall in the path #
        #################################################################
        new_position = self.switch_position_on_wall_contact(current_position)
        if new_position != current_position:
            print(
                f"get_next_move_with_AI: Updated current position from {current_position} to {new_position} after wall contact.")
            current_position = new_position

        print(f"get_next_move_with_AI: Current position before step 1 : {current_position}")

        ##############################################################################
        # If Red AI makes first move as wall-adjacent go to detect and evaluate bridges #
        ##############################################################################
        if playerColor == "Red":
            if current_position < self.board_size:
                print(
                    f"get_next_move_with_AI STEP 1: Current Position {current_position} for red is next to top wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index

            if current_position >= self.board_size * (self.board_size - 1):
                print(
                    f"get_next_move_with_AI: STEP 1: Current Position {current_position} for red is next to bottom wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index

        ##################################################################################
        # If Blue AI makes first move as wall-adjacent go to detect and evaluate bridges #
        ##################################################################################
        if playerColor == "Blue":
            if current_position % self.board_size == 0:
                print(
                    f"get_next_move_with_AI: STEP 1: Current Position {current_position} for blue is next to left wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index
            if current_position % self.board_size == self.board_size - 1:
                print(
                    f"get_next_move_with_AI: STEP 1: Current Position {current_position} for blue is next to right wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index

        print(f"Current position before step 2 : {current_position}")
        print(f"get_next_move_with_AI: Current position before step 2 : {current_position}")

        ###############################################################################
        # Checks if a neigbour is wall adjecent, then return that index as move index #
        ###############################################################################
        neighbor_with_wall = self.detect_neighbours_is_with_wall(current_position)
        print(f"get_next_move_with_AI: STEP 2: Detected wall-adjacent neighbor: {neighbor_with_wall}")
        if neighbor_with_wall is not None and neighbor_with_wall not in self.MoveList:
            print(
                f"get_next_move_with_AI: STEP 2: Returning wall-adjacent neighbor {neighbor_with_wall} as the next move")
            return neighbor_with_wall  # End the function here if a wall-adjacent neighbor is found
        print("get_next_move_with_AI: STEP 2/3:  No wall-adjacent neighbors detected, proceeding to bridge detection")

        ##################################
        # Calls detetect bridge function #
        ##################################
        self.detect_bridge(current_position)

        #########################################################################################################
        # If current position has detected bridge pattern, find best bridge pattern and return it as move index #
        #########################################################################################################
        possible_bridges = self.PossibleBridgesList[current_position]
        if possible_bridges:
            print(
                f"get_next_move_with_AI: STEP 3:  All possible bridges detected in {current_position} are: {possible_bridges}, will now evaluate them to pick the best one.")
            index = self.evaluate_bridge(current_position)
            return index

        #########################################################################################################
        # If current position has has no bridge patterns, find the free neigbour closest to opposite wall  #
        #########################################################################################################
        closest_opposite_wall_index = self.opposite_wall_cloesest_index(current_position)
        if closest_opposite_wall_index:
            print("get_next_move_with_AI: STEP 3:  no bridgesfound , retuning index as none")
            return index
        else:
            index = None

        return index

    def opposite_wall_cloesest_index(self, current_position):

        neighbours = self.all_edges[current_position]

        print(f"opposite_wall_cloesest_index: neighbours for {current_position}: {neighbours}")

        top_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if index < self.board_size]
        bot_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if
                          index >= self.board_size * (self.board_size - 1)]

        touching_top_wall = False
        for node in self.Current_Winning_Path:
            if node in top_wall_nodes:
                print(
                    f"opposite_wall_cloesest_index: top_wall_nodes: {top_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_top_wall = True

        touching_bot_wall = False
        for node in self.Current_Winning_Path:
            if node in bot_wall_nodes:
                print(
                    f"opposite_wall_cloesest_index: bot_wall_nodes: {bot_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_bot_wall = True

        if touching_bot_wall is True:
            lowest_neighbour = min(neighbours)
            if self.CellNodesFeatureList[lowest_neighbour] == "None":
                index = lowest_neighbour
                print(f"opposite_wall_cloesest_index: chose {index} as move since its closest to top wall ")
                return index

        if touching_top_wall is True:
            highest_neighbour = max(neighbours)
            if self.CellNodesFeatureList[highest_neighbour] == "None":
                index = highest_neighbour
                print(f"opposite_wall_cloesest_index: chose {index} as move since its closest to bot wall ")
                return index

        return None

    def detect_paths(self):
        # Changes the cells to corresponding player color: Red or Blue
        if self.Player1:
            current_player_color = "Blue"
        else:
            current_player_color = "Red"
         

            
        if current_player_color == "Red":
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

                    # Handle direct adjacency connection (neighboring nodes)
                    if next_red_index in edges_for_index_i:
                        print(
                            f"detect_paths: Bonded path exists between red index {red_index} and red index {next_red_index} (neighbors).")
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

                    shared_edges = edges_for_index_i.intersection(edges_for_next_index)
                    shared_edges_list = list(shared_edges)

                    if len(shared_edges_list) == 2:
                        print(f"detect_paths: Shared edges: {shared_edges_list}")

                        cell_status_1 = self.CellNodesFeatureList[shared_edges_list[0]]
                        cell_status_2 = self.CellNodesFeatureList[shared_edges_list[1]]

                        if cell_status_1 == "None" and cell_status_2 == "None":

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

                    print(
                        f"detect_paths: Evaluating path {path}: min index = {min_index}, max index = {max_index}, coverage = {coverage}")

                    # Update if this path has the longest coverage seen so far
                    if coverage > max_coverage:
                        max_coverage = coverage
                        longest_path = path

            # Print the path with the longest top-to-bottom coverage
            if longest_path is not None:
                self.Current_Winning_Path = longest_path
                print(
                    f"\ndetect_paths: The path with the longest top-to-bottom coverage is: {longest_path} with coverage of {max_coverage}")
            else:
                print("\ndetect_paths: No valid paths found.")
                self.Current_Winning_Path = []

            # Final output of all unique paths
            print("\ndetect_paths: Final Red paths with unique pairs:")
            print(self.RedPaths)



        if current_player_color == "Blue":
            # Get all red indexes from CellNodesFeatureList
            blue_indexes = [index for index, value in enumerate(self.CellNodesFeatureList) if value == "Blue"]
            print(f"detect_paths: All the blue indexes in CellNodeFeatureList are at: {blue_indexes}")

        
            # For loop going through all blue indexes and getting their edges
            for blue_index in blue_indexes:
                blue_edges = self.all_edges[blue_index]
                self.blue_edges_mapping[blue_index] = list(blue_edges)

            # Prints out all the red indexes with their corresponding edges from the list red_edges_mapping
            print("\ndetect_paths: Blue indexes with their edges:")
            for index, edges in enumerate(self.blue_edges_mapping):
                if edges:  # Only print non-empty entries for clarity
                    print(f"detect_paths: Index {index}: {edges}")


            # Check for paths between each pair of red nodes
            print("\ndetect_paths: Paths between blue nodes:")


            for i, red_index in enumerate(blue_indexes):
                edges_for_index_i = set(self.blue_edges_mapping[blue_index])
                print(f"\ndetect_paths: Current Position being evaluated: {blue_index} for bLUE")
                print(f"detect_paths: Edges for blue index {blue_index}: {edges_for_index_i}")


                # Compare with subsequent red indexes to check for paths
                for j in range(i + 1, len(blue_indexes)):
                    next_blue_index = blue_indexes[j]

                    edges_for_next_index = set(self.blue_edges_mapping[next_blue_index])

                    # Find common edges between blue_index and next_blue_index

                    # Handle direct adjacency connection (neighboring nodes)

                    if next_blue_index in edges_for_index_i:
                        print( f"detect_paths: Bonded path exists between blue index {blue_index} and blue index {blue_index} (neighbors).")
                        path_found = False


                       # Search for existing path that includes red_index or next_red_index
                        for path in self.BluePaths:
                            if blue_index in path or next_blue_index in path:
                                # Extend the existing path with any new unique nodes
                                if blue_index not in path:
                                    path.append(blue_index)
                                if next_blue_index not in path:
                                    path.append(next_blue_index)
                                path_found = True
                                print(f"detect_paths: Added {blue_index} and {next_blue_index} to existing path: {path}")
                                break

                        # If no path was found, create a new separate path for these connected nodes
                        if not path_found:
                            self.BluePaths.append([blue_index, next_blue_index])
                            print(f"detect_paths: Created new path: [{blue_index}, {next_blue_index}]")



                    shared_edges = edges_for_index_i.intersection(edges_for_next_index)
                    shared_edges_list = list(shared_edges)

                    if len(shared_edges_list) == 2:
                        print(f"detect_paths: Shared edges: {shared_edges_list}")

                        cell_status_1 = self.CellNodesFeatureList[shared_edges_list[0]]
                        cell_status_2 = self.CellNodesFeatureList[shared_edges_list[1]]
        


                        if cell_status_1 == "None" and cell_status_2 == "None":

                            path_found = False

                            # Search for an existing path that includes red_index or next_red_index
                            for path in self.BluePaths:
                                if blue_index in path or next_blue_index in path:
                                    # Extend the existing path with any new unique nodes
                                    if blue_index not in path:
                                        path.append(blue_index)
                                    if next_blue_index not in path:
                                        path.append(next_blue_index)
                                    path_found = True
                                    break

                            # If no path was found, create a new separate path for these nodes
                            if not path_found:
                                self.BluePaths.append([blue_index, next_blue_index])
                                print(f"detect_paths: Created new path: [{blue_index}, {next_blue_index}]")


            # Step: Find the path with the longest top-to-bottom coverage
            longest_path = None
            max_coverage = 0
            self.Current_Winning_Path = []


            for path in self.BluePaths:
                if path:
                    min_index = min(path)
                    max_index = max(path)
                    coverage = max_index - min_index

                    print(
                        f"detect_paths: Evaluating path {path}: min index = {min_index}, max index = {max_index}, coverage = {coverage}")

                    # Update if this path has the longest coverage seen so far
                    if coverage > max_coverage:
                        max_coverage = coverage
                        longest_path = path




            # Print the path with the longest top-to-bottom coverage
            if longest_path is not None:
                self.Current_Winning_Path = longest_path
                print(
                    f"\ndetect_paths: The path with the longest top-to-bottom coverage is: {longest_path} with coverage of {max_coverage}")
            else:
                print("\ndetect_paths: No valid paths found.")
                self.Current_Winning_Path = []

            # Final output of all unique paths
            print("\ndetect_paths: Final Blue paths with unique pairs:")
            print(self.BluePaths)





    def winning_path(self):
        # Check if any position in current_winning_path touches the top wall

        top_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if index < self.board_size]
        bot_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if
                          index >= self.board_size * (self.board_size - 1)]

        touching_top_wall = False
        for node in self.Current_Winning_Path:
            if node in top_wall_nodes:
                print(
                    f"current_winning_path: top_wall_nodes: {top_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_top_wall = True

        touching_bot_wall = False
        for node in self.Current_Winning_Path:
            if node in bot_wall_nodes:
                print(
                    f"current_winning_path: bot_wall_nodes: {bot_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_bot_wall = True

        # Combined condition to check if the path touches both the top and bottom walls
        if touching_top_wall is True and touching_bot_wall is True:
            print(f"current_winning_path {self.Current_Winning_Path} is touching both the top and bottom walls.")



            # Confirm that the path is fully connected in a bridge pattern
            fully_connected = True

            for i in range(len(self.Current_Winning_Path)):
                for j in range(i + 1, len(self.Current_Winning_Path)):  # Avoid duplicates by starting from i+1
                    node_a = self.Current_Winning_Path[i]
                    node_b = self.Current_Winning_Path[j]

                    # Find shared edges (bridge connections) between node_a and node_b
                    neighbors_a = set(self.red_edges_mapping[node_a])
                    neighbors_b = set(self.red_edges_mapping[node_b])
                    shared_edges = neighbors_a.intersection(neighbors_b)
                    shared_edges_list = list(shared_edges)

                    print(f"current_winning_path: shared_edges_list: {shared_edges_list}")
                    # If fully connected, then proceed to fill
                    if fully_connected:

                        if len(shared_edges_list) <= 1:
                            continue

                        if len(shared_edges_list) == 2:
                            if shared_edges_list[0] not in self.all_edges[shared_edges_list[1]]:
                                print("current_winning_path: This is not a bridge pattern")
                                continue

                        if (self.CellNodesFeatureList[shared_edges_list[0]] == "Red" or self.CellNodesFeatureList[
                            shared_edges_list[1]] == "Red"):
                            continue

                        if (self.CellNodesFeatureList[shared_edges_list[0]] == "None" and self.CellNodesFeatureList[
                            shared_edges_list[1]] == "None"):
                            fill_bp_index = choice(shared_edges_list)
                            print(f"current_winning_path: Filled edge {fill_bp_index} between nodes {node_a} and {node_b}.")
                            return fill_bp_index
        return None

    def disrupted_paths(self):
        current_player_color = "Blue"

        if self.Player1:
            current_player_color = "Red"
        else:
            current_player_color = "Blue"

        for i in range(len(self.Current_Winning_Path)):
            for j in range(i + 1, len(self.Current_Winning_Path)):  # Avoid duplicates by starting from i+1
                print(f"disrupted_paths -> Current_Winning_Path: {self.Current_Winning_Path}")

                node_a = self.Current_Winning_Path[i]
                node_b = self.Current_Winning_Path[j]

                # Find shared edges (bridge connections) between node_a and node_b
                neighbors_a = set(self.red_edges_mapping[node_a])
                neighbors_b = set(self.red_edges_mapping[node_b])
                shared_edges = neighbors_a.intersection(neighbors_b)
                shared_edges_list = list(shared_edges)

                # Initialize variables to track the status of shared edges
                occupied_by_opponent = None  # Index of a cell occupied by opponent
                occupied_by_self = False  # Flag to indicate if any cell is occupied by the current player
                unoccupied_index = None  # Index of an unoccupied cell

                print(f"disrupted_paths: Shared edges list: {shared_edges_list}")
                print(f"disrupted_paths: Length of Shared edges list: {len(shared_edges_list)}")

                if len(shared_edges_list) < 1:
                    print(f"disrupted_paths: Self.all_edges[[shared_edges_list[1]]]: Empty")
                    continue

                if len(shared_edges_list) == 2:
                    # If the first second in shared_edges_list is not an edge for first shared_edges_list index
                    if shared_edges_list[1] not in self.all_edges[shared_edges_list[0]]:
                        print("disrupted_paths: This is not a bridge pattern the disruption is happening at2")
                        continue

                if len(shared_edges_list) == 2:
                    # If the first index in shared_edges_list is not an edge for second shared_edges_list index
                    if shared_edges_list[0] not in self.all_edges[shared_edges_list[1]]:
                        print("disrupted_paths: This is not a bridge pattern the disruption is happening at1")
                        continue

                # Assuming `current_player_color` holds the current player's color (e.g., "Red" or "Blue")
                for edge in shared_edges_list:
                    cell_status = self.CellNodesFeatureList[edge]

                    if cell_status == "None":
                        unoccupied_index = edge  # Track an unoccupied cell index
                    elif cell_status == current_player_color:
                        occupied_by_self = True  # Mark that a cell is occupied by the current player
                    else:
                        occupied_by_opponent = edge  # Track opponent's occupied cell

                # Determine the outcome based on occupancy status
                if occupied_by_self:
                    # Continue if any shared edge cell is occupied by the current player's piece
                    print("disrupted_paths: One of the cells is occupied by the current player's piece.")
                    continue
                elif occupied_by_opponent is not None and unoccupied_index is not None:
                    # Return the unoccupied cell index if only one cell is occupied by the opponent
                    print(f"disrupted_paths: Returning unoccupied cell index {unoccupied_index}.")
                    return unoccupied_index
                elif occupied_by_opponent is not None and unoccupied_index is None:
                    # If both cells are occupied (by opponent or otherwise), return None
                    print("disrupted_paths: Both shared edge cells are occupied. Returning None.")
                    return None
                else:
                    # No specific conditions met; return None as a default
                    print("disrupted_paths: No conditions met. Returning None.")
                    continue

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
        touching_top_wall = False
        touching_bot_wall = False

        # Check the Red_Paths for wall touching nodes
        for path in self.RedPaths:
            if current_position in path:
                top_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if index < self.board_size]
                bot_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if
                                  index >= self.board_size * (self.board_size - 1)]

                for node in self.Current_Winning_Path:
                    if node in top_wall_nodes:
                        print(
                            f"switch_position_on_wall_contact: top_wall_nodes: {top_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                        touching_top_wall = True

                for node in self.Current_Winning_Path:
                    if node in bot_wall_nodes:
                        print(
                            f"switch_position_on_wall_contact: bot_wall_nodes: {bot_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                        touching_bot_wall = True

                break

        # Collect neighbors that are touching the top or bottom wall
        wall_adjacent_neighbors = []
        for neighbor in neighbours:

            if neighbor < self.board_size:
                if touching_top_wall is False:
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the top wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(
                        f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the top wall, but a top wall touching index already exists in the path. Skipping.")

            elif neighbor >= self.board_size * (self.board_size - 1):
                if touching_bot_wall is False:
                    print(f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the bottom wall.")
                    wall_adjacent_neighbors.append(neighbor)
                else:
                    print(
                        f"switch_position_on_wall_contact: Neighbor {neighbor} is touching the bottom wall, but a bottom wall touching index already exists in the path. Skipping.")

        return current_position  # Return current position if no wall contact switch is needed

    def detect_neighbours_is_with_wall(self, current_position):
        index = None
        neighbours = self.all_edges[current_position]
        playerColor = self.CellNodesFeatureList[current_position]

        wall_adjacent_neighbors = []

        # Check if current_position is part of a path that already touches the top wall
        #        if playerColor == "Red" and hasattr(self, 'current_winning_path'):
        if playerColor == "Red":

            top_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if index < self.board_size]
            bot_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if
                              index >= self.board_size * (self.board_size - 1)]

            touching_top_wall = False
            for node in self.Current_Winning_Path:
                if node in top_wall_nodes:
                    print(
                        f"detect_neighbours_is_with_wall: top_wall_nodes: {top_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                    touching_top_wall = True

            touching_bot_wall = False
            for node in self.Current_Winning_Path:
                if node in bot_wall_nodes:
                    print(
                        f"detect_neighbours_is_with_wall: bot_wall_nodes: {bot_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                    touching_bot_wall = True

            """
            if touching_top_wall is True:
                print(
                    f"detect_neighbours_is_with_wall: Current position {current_position} is in a path that already touches the top wall. Skipping wall-adjacent neighbors.")
                return None  # Skip adding wall-adjacent neighbors if already touching the top wall


            if touching_bot_wall is True:
                print(
                    f"detect_neighbours_is_with_wall: Current position {current_position} is in a path that already touches the top wall. Skipping wall-adjacent neighbors.")
                return None  # Skip adding wall-adjacent neighbors if already touching the top wall
            """

        if playerColor == "Red":
            for neighbor in neighbours:
                # if neigbour is touching top wall and is empty and the current positions is in a path that is not touching top wall: append that neibour
                if neighbor < self.board_size and self.CellNodesFeatureList[
                    neighbor] == "None" and touching_top_wall is False:
                    print(f"check_if_neighbours_is_with_wall: Neighbor {neighbor} is touching the top wall.")
                    wall_adjacent_neighbors.append(neighbor)

                # if neigbour is touching bot wall and is empty and the current positions is in a path that is not touching bot wall: append that neibour
                elif neighbor >= self.board_size * (self.board_size - 1) and self.CellNodesFeatureList[
                    neighbor] == "None" and touching_bot_wall is False:
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

        # if there are neighbours that are wall-adjacent, chose them as an index, if there are multiple, pick one of them
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
            # if neigbours are touching the top wall wall wall, append those neigbours indexes in wall_adjacent_neigbour
            if neighbor < self.board_size:
                wall_adjacent_neighbors.append(neighbor)
            # if neigbours are touching the bottom wall wall wall, append those neigbours indexes in wall_adjacent_neigbour
            elif neighbor >= self.board_size * (self.board_size - 1):
                wall_adjacent_neighbors.append(neighbor)

        # if there are neigbours that are wall-adjacent, chose them as an index, if there are multiple, pick one of them
        if wall_adjacent_neighbors:
            index = choice(wall_adjacent_neighbors)

        return index

    # detects bridges for current position
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
            if 0 <= bp_top_index < len(self.CellNodesFeatureList) and 0 <= top_r_index < len(
                    self.CellNodesFeatureList) and 0 <= top_l_index < len(
                    self.CellNodesFeatureList) and index % board_size != board_size - 1:  # Ensure index is not on the right edge
                if self.CellNodesFeatureList[bp_top_index] == "None" and self.CellNodesFeatureList[
                    top_r_index] == "None" and self.CellNodesFeatureList[top_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_index)

                else:
                    if self.CellNodesFeatureList[top_r_index] == "None":
                        self.PossibleBridgesList[index].append(top_r_index)
                    if self.CellNodesFeatureList[top_l_index] == "None":
                        self.PossibleBridgesList[index].append(top_l_index)

        # Check if upper right bridge pattern is possible
        if index >= board_size and index % self.board_size < (self.board_size - 2):
            bp_top_right_index = (index - self.board_size + 2)
            up_l_index = (index - self.board_size + 1)
            up_r_index = (index + 1)
            if 0 <= bp_top_right_index < len(self.CellNodesFeatureList) and 0 <= up_l_index < len(
                    self.CellNodesFeatureList) and 0 <= up_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_right_index] == "None" and self.CellNodesFeatureList[
                    up_l_index] == "None" and self.CellNodesFeatureList[up_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_right_index)

        # Check if the upper left bridge pattern is possible
        if index >= board_size and index % self.board_size > 0:
            bp_top_left_index = (index - board_size - 1)
            up_l_up_index = (index - board_size)
            up_l_down_index = (index - 1)
            if 0 <= bp_top_left_index < len(self.CellNodesFeatureList) and 0 <= up_l_up_index < len(
                    self.CellNodesFeatureList) and 0 <= up_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_left_index] == "None" and self.CellNodesFeatureList[
                    up_l_up_index] == "None" and self.CellNodesFeatureList[up_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_left_index)
                else:
                    if self.CellNodesFeatureList[up_l_up_index] == "None":
                        self.PossibleBridgesList[index].append(up_l_up_index)
                    if self.CellNodesFeatureList[up_l_down_index] == "None":
                        self.PossibleBridgesList[index].append(up_l_down_index)

        # Check if most down bridge pattern is possible
        if index < board_size * (
                board_size - 2) and index % self.board_size > 0:  # Ensure not in the last two rows and at least one position away from the left edge
            bp_bot_index = (index + 2 * self.board_size - 1)
            bot_r_index = (index + self.board_size - 1)
            bot_l_index = (index + self.board_size)
            if (0 <= bp_bot_index < len(self.CellNodesFeatureList) and 0 <= bot_r_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_l_index < len(
                    self.CellNodesFeatureList) and index % self.board_size != (self.board_size + 2)):
                if self.CellNodesFeatureList[bp_bot_index] == "None" and self.CellNodesFeatureList[
                    bot_r_index] == "None" and self.CellNodesFeatureList[bot_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_index)


                else:
                    if self.CellNodesFeatureList[bot_r_index] == "None":
                        self.PossibleBridgesList[index].append(bot_r_index)
                    if self.CellNodesFeatureList[bot_l_index] == "None":
                        self.PossibleBridgesList[index].append(bot_l_index)

        # Check if the bottom right bridge pattern is possible
        if index < board_size * (board_size - 1) and index % self.board_size < (
                self.board_size - 1):  # Ensure not in the last row and at least one position away from the right edge
            bp_bot_right_index = (index + board_size + 1)
            bot_l_index = (index + board_size)
            bot_r_index = (index + 1)
            if 0 <= bp_bot_right_index < len(self.CellNodesFeatureList) and 0 <= bot_l_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_right_index] == "None" and self.CellNodesFeatureList[
                    bot_l_index] == "None" and self.CellNodesFeatureList[bot_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_right_index)
                else:
                    if self.CellNodesFeatureList[bot_l_index] == "None":
                        self.PossibleBridgesList[index].append(bot_l_index)
                    if self.CellNodesFeatureList[bot_r_index] == "None":
                        self.PossibleBridgesList[index].append(bot_r_index)

        # Check if the bottom left bridge pattern is possible
        if index < board_size * (
                board_size - 1) and index % self.board_size > 1:  # Ensure not in the last row and at least two positions away from the left edge
            bp_bot_left_index = (index + board_size - 2)
            bot_l_down_index = (index + board_size - 1)
            bot_l_up_index = (index - 1)
            if 0 <= bp_bot_left_index < len(self.CellNodesFeatureList) and 0 <= bot_l_up_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_left_index] == "None" and self.CellNodesFeatureList[
                    bot_l_up_index] == "None" and self.CellNodesFeatureList[bot_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_left_index)
        playerColor = self.CellNodesFeatureList[index]
        board_size = self.board_size
        self.PossibleBridgesList[index].clear()
        print(f"detect_bridge: Evaluating bridge patterns for index {index} with color {playerColor}")

        # Check if the most upper bridge pattern is possible
        if index >= board_size * 2 and index % self.board_size < (self.board_size - 1):
            bp_top_index = (index - 2 * board_size + 1)
            top_r_index = (index - board_size + 1)
            top_l_index = (index - board_size)
            if 0 <= bp_top_index < len(self.CellNodesFeatureList) and 0 <= top_r_index < len(
                    self.CellNodesFeatureList) and 0 <= top_l_index < len(
                    self.CellNodesFeatureList) and index % board_size != board_size - 1:  # Ensure index is not on the right edge
                if self.CellNodesFeatureList[bp_top_index] == "None" and self.CellNodesFeatureList[
                    top_r_index] == "None" and self.CellNodesFeatureList[top_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_index)

        # Check if upper right bridge pattern is possible
        if index >= board_size and index % self.board_size < (self.board_size - 2):
            bp_top_right_index = (index - self.board_size + 2)
            up_l_index = (index - self.board_size + 1)
            up_r_index = (index + 1)
            if 0 <= bp_top_right_index < len(self.CellNodesFeatureList) and 0 <= up_l_index < len(
                    self.CellNodesFeatureList) and 0 <= up_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_right_index] == "None" and self.CellNodesFeatureList[
                    up_l_index] == "None" and self.CellNodesFeatureList[up_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_right_index)

        # Check if the upper left bridge pattern is possible
        if index >= board_size and index % self.board_size > 0:
            bp_top_left_index = (index - board_size - 1)
            up_l_up_index = (index - board_size)
            up_l_down_index = (index - 1)
            if 0 <= bp_top_left_index < len(self.CellNodesFeatureList) and 0 <= up_l_up_index < len(
                    self.CellNodesFeatureList) and 0 <= up_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_top_left_index] == "None" and self.CellNodesFeatureList[
                    up_l_up_index] == "None" and self.CellNodesFeatureList[up_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_left_index)

        # Check if most down bridge pattern is possible
        if index < board_size * (
                board_size - 2) and index % self.board_size > 0:  # Ensure not in the last two rows and at least one position away from the left edge
            bp_bot_index = (index + 2 * self.board_size - 1)
            bot_r_index = (index + self.board_size - 1)
            bot_l_index = (index + self.board_size)
            if (0 <= bp_bot_index < len(self.CellNodesFeatureList) and 0 <= bot_r_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_l_index < len(
                    self.CellNodesFeatureList) and index % self.board_size != (self.board_size + 2)):
                if self.CellNodesFeatureList[bp_bot_index] == "None" and self.CellNodesFeatureList[
                    bot_r_index] == "None" and self.CellNodesFeatureList[bot_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_index)

        # Check if the bottom right bridge pattern is possible
        if index < board_size * (board_size - 1) and index % self.board_size < (
                self.board_size - 1):  # Ensure not in the last row and at least one position away from the right edge
            bp_bot_right_index = (index + board_size + 1)
            bot_l_index = (index + board_size)
            bot_r_index = (index + 1)
            if 0 <= bp_bot_right_index < len(self.CellNodesFeatureList) and 0 <= bot_l_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_r_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_right_index] == "None" and self.CellNodesFeatureList[
                    bot_l_index] == "None" and self.CellNodesFeatureList[bot_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_right_index)

        # Check if the bottom left bridge pattern is possible
        if index < board_size * (
                board_size - 1) and index % self.board_size > 1:  # Ensure not in the last row and at least two positions away from the left edge
            bp_bot_left_index = (index + board_size - 2)
            bot_l_down_index = (index + board_size - 1)
            bot_l_up_index = (index - 1)
            if 0 <= bp_bot_left_index < len(self.CellNodesFeatureList) and 0 <= bot_l_up_index < len(
                    self.CellNodesFeatureList) and 0 <= bot_l_down_index < len(self.CellNodesFeatureList):
                if self.CellNodesFeatureList[bp_bot_left_index] == "None" and self.CellNodesFeatureList[
                    bot_l_up_index] == "None" and self.CellNodesFeatureList[bot_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_left_index)

    def evaluate_bridge(self, current_position):
        selected_pattern = None

        print(f"evaluate_bridge: Evaluate bridge happening from starting index: {current_position}")

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        if not bridge_patterns:
            print(f"evaluate_bridge: No bridge patterns found in PossibleBridgesList")

        # Check if any position in current_winning_path touches the top wall

        top_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if index < self.board_size]
        bot_wall_nodes = [index for index in range(len(self.CellNodesEdgeList)) if
                          index >= self.board_size * (self.board_size - 1)]

        touching_top_wall = False
        for node in self.Current_Winning_Path:
            if node in top_wall_nodes:
                print(
                    f"evaluate_bridge: top_wall_nodes: {top_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_top_wall = True

        touching_bot_wall = False
        for node in self.Current_Winning_Path:
            if node in bot_wall_nodes:
                print(
                    f"evaluate_bridge: bot_wall_nodes: {bot_wall_nodes} and for current path: {self.Current_Winning_Path} the node {node}")
                touching_bot_wall = True

        # Combined condition to check if the path touches both the top and bottom walls
        if touching_top_wall is True and touching_bot_wall is True:
            print(f"evaluate_bridge: {self.Current_Winning_Path} is touching both the top and bottom walls.")

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":
                print(f"Evaluate bridge happening from {self.CellNodesFeatureList[current_position]}")

                # Filter out bridge patterns that would lead to top wall positions if the path touches the top wall
                if touching_top_wall is True:
                    print(f"Bridge_Patter_Lis_TopWall: {bridge_patterns}")
                    print(
                        f"evaluate_bridge: hei Path containing {current_position} touches the top wall. Filtering out bridges to top wall positions.")

                    selected_pattern = max(bridge_patterns)

                    self.Red_Bp.append(selected_pattern)
                    print(
                        f"evaluate_bridge: hei Selected highest index pattern: {selected_pattern} from possible patterns {bridge_patterns}")
                # Prioritize lowest bridge pattern for upward movement if path touches the bottom wall
                if touching_bot_wall is True:
                    print(f"Bridge_Patter_Lis_BottomWall: {bridge_patterns}")
                    print(
                        f"evaluate_bridge: hei Path containing {current_position} touches the bottom wall. Prioritizing the lowest bridge pattern for upward movement.")
                    selected_pattern = min(bridge_patterns)  # Choose the bridge pattern with the lowest index
                    print(
                        f"evaluate_bridge: hei Selected lowest index pattern: {selected_pattern} from possible patterns {bridge_patterns}")
                    self.Red_Bp.append(selected_pattern)
                else:
                    # Distance of detected bp from current position
                    distances = [(x, abs(x - current_position)) for x in bridge_patterns]
                    # Find the longest distance from current position regardless of if its over or under the current
                    max_distance = max(distances, key=lambda x: x[1])[1]
                    # Get all bridge patterns that are at the maximum distance
                    farthest_patterns = [x[0] for x in distances if x[1] == max_distance]

                    # Goes through list of bridge patterns in current position and does an if check
                    # If a bp index touching a top or bottom wall, choose that as the index
                    for pattern in bridge_patterns:
                        # the bp is touching top wall and current position is in a path that is not touching top wall
                        if pattern < self.board_size and touching_top_wall is False:
                            selected_pattern = pattern
                            self.Red_Bp.append(selected_pattern)

                            print(
                                f"evaluate_bridge: Selected top-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break
                        if pattern >= self.board_size * (self.board_size - 1) and touching_bot_wall is False:
                            selected_pattern = pattern
                            self.Red_Bp.append(selected_pattern)
                            print(
                                f"evaluate_bridge: Selected bottom-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break

                    # Default to a random farthest pattern if no suitable pattern is found
                    if selected_pattern is None and farthest_patterns:
                        selected_pattern = choice(farthest_patterns)
                        self.Red_Bp.append(selected_pattern)
                        print(
                            f"evaluate_bridge: Selected farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                    print(
                        f"evaluate_bridge: Red selected bridge pattern index: {selected_pattern} from possible patterns {bridge_patterns}")

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
                            print(
                                f"evaluate_bridge: Selected left-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                            break
                        if pattern % self.board_size == self.board_size - 1:
                            selected_pattern = pattern
                            print(
                                f"evaluate_bridge: Selected right-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
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

    # check if the current position(index being evalueted) is touching the top or bot wall
    def check_top_bottom_wall_NO_PRINT(self, index):
        current_position = self.MoveList[-2]

        if current_position < self.board_size:
            return True
        elif current_position >= self.board_size * (self.board_size - 1):
            return True
        return False




































