from random import choice



class BP:

    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list, move_list, All_Edges,  RedAI, BlueAI):
        self.board_size = size
        self.Player1 = True
        self.Winner = None
        self.redAI = RedAI
        self.blueAI = BlueAI


        # Create an array containing arrays
        # A single array represents a cell in the hex game
        # This array of array represents the features of a cell
        self.CellNodesFeatureList = cell_node_feature_list

        # Creates an array containing arrays
        # A single array in the array represents the connections of a cell with the same symbol
        self.CellNodesEdgeList = cell_nodes_edge_list

        # Array that contains a moves done
        self.MoveList = move_list

        self.all_edges = All_Edges

        # Array that contains the possible bridges
        self.PossibleBridgesList = [[] for _ in range(self.board_size * self.board_size)]

        self.Red_Bp = [[] for _ in range(self.board_size * self.board_size)]

        self.Blue_Bp = [[] for _ in range(self.board_size * self.board_size)]

        return



    def get_next_move(self):
        index = None

        if len(self.MoveList) < 2:
            print("\nGetNextMove: Both players need to make at least one move")
            return None

        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]
        print(f"get_next_move: Current Position being evaluated: {current_position} for {playerColor} ")

        if playerColor == "Red":
            if self.redAI:
                print("Red is using AI")
                index = self.get_next_move_with_AI()
            else:
                print("Red is not using AI")

        if playerColor == "Blue":
            if self.blueAI:
                print("Blue is using AI")
                index = self.get_next_move_with_AI()
            else:
                print("Blue is not using AI")

        return index


    def get_next_move_with_AI(self):
        index = None
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]



        # Step 1: If current index is next their given wall, go to evaluate bridge
        if playerColor == "Red":
            # Step 1: If current position is touching a wall go to detect and evaluate bridge:
            if current_position < self.board_size:
                print(f"get_next_move: STEP 1: Current Position {current_position} for red is next to top wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index
            if current_position >= self.board_size * (self.board_size - 1):
                print(f"get_next_move: STEP 1: Current Position {current_position} for red is next to bottom wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index


        if playerColor == "Blue":
            if current_position % self.board_size == 0:
                print(f"get_next_move: STEP 1: Current Position {current_position} for blue is next to left wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index
            if current_position % self.board_size == self.board_size - 1:
                print(f"get_next_move: STEP 1: Current Position {current_position} for blue is next to right wall, go to evaluate bridge: ")
                index = self.evaluate_bridge(current_position)
                return index



        # Step 2: If a wall-adjacent neighbor is detected, return that neighbor as Index
        neighbor_with_wall = self.detect_neighbours_is_with_wall(current_position)
        print(f"get_next_move: STEP 2: Detected wall-adjacent neighbor: {neighbor_with_wall}")

        if neighbor_with_wall is not None and neighbor_with_wall not in self.MoveList:
            print(f" STEP 2: get_next_move: Returning wall-adjacent neighbor {neighbor_with_wall} as the next move")
            return neighbor_with_wall  # End the function here if a wall-adjacent neighbor is found

        print("get_next_move: STEP 2/3:  No wall-adjacent neighbors detected, proceeding to bridge detection")

        # Step 3: Check if current position has detected bridges , if so evaluate them
        self.detect_bridge(current_position)
        possible_bridges = self.PossibleBridgesList[current_position]

        if possible_bridges:  # Checks if possible_bridges is non-empty
            print(f"get_next_move: STEP 3:  All possible bridges detected in {current_position} are: {possible_bridges}, will now evaluate them to pick the best one.")
            index = self.evaluate_bridge(current_position)
            return index
        else:
            print("get_next_move: STEP 3:  No possible bridges found")


        return index


    #checks if any neigbours of the current position are touching the top or bottom wall
    def detect_neighbours_is_with_wall(self, index):
        index = None
        current_position = self.MoveList[-2]
        neighbours = self.all_edges[current_position]
        playerColor = self.CellNodesFeatureList[current_position]
        wall_adjacent_neighbors = []

        if playerColor == "Red":
            for neighbor in neighbours:
                #if neighbours are touching the top wall , append those neighbours indexes in wall_adjacent_neighbours
                if neighbor < self.board_size:
                        print(f"check_if_neighbours_is_with_wall: Neighbor {neighbor} is touching the top wall.")
                        wall_adjacent_neighbors.append(neighbor)

                #if neighbours are touching the bottom wall, append those neighbours indexes in wall_adjacent_neighbours
                elif neighbor >= self.board_size * (self.board_size - 1):
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



    def evaluate_bridge(self, selected_pattern):
        current_position = self.MoveList[-2]
        selected_pattern = None

        print(f"evaluate_bridge: Evaluate bridge happening from starting index: {current_position}")

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        if not bridge_patterns:
            print(f"evaluate_bridge: No bridge patterns found in PossibleBridgesList")

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":

                print(f"Evaluate bridge happening from {self.CellNodesFeatureList[current_position]}")

                # Distance of detected bp from current position

                distances = [(x, abs(x - current_position)) for x in bridge_patterns]
                # Find the longest distance from current position regardless of if its over or under the current
                max_distance = max(distances, key=lambda x: x[1])[1]
                # Get all bridge patterns that are at the maximum distance
                farthest_patterns = [x[0] for x in distances if x[1] == max_distance]

                #Goes through list of bridge patterns in current position and does an if check
                #If a bp index touching a top or bottom wall, choose that as the index
                for pattern in bridge_patterns:
                    # Check if the pattern is wall-adjacent based on downward movement preference
                    if  pattern < self.board_size:
                        selected_pattern = pattern
                        print(f"evaluate_bridge: Selected top-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                        break
                    if  pattern >= self.board_size * (self.board_size - 1):
                        selected_pattern = pattern
                        print(f"evaluate_bridge: Selected bottom-wall-adjacent farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
                        break
                # Default to a random farthest pattern if no suitable pattern is found
                if selected_pattern is None:
                    selected_pattern = choice(farthest_patterns)
                    print(
                        f"evaluate_bridge: Selected farthest index: {selected_pattern} from possible patterns {bridge_patterns}")
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

















