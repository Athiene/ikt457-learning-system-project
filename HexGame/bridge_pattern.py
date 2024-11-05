from random import choice


class BP:


    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list, move_list, red_bp, blue_bp):
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


        # Array that contains a moves done
        self.MoveList = move_list

        # Array that contains the possible bridges
        self.PossibleBridgesList = [[] for _ in range(self.board_size * self.board_size)]

        # Initialize Red_Bp and Blue_Bp as lists of lists
        self.Red_Bp = red_bp

        self.Blue_Bp = blue_bp



        return



    def get_next_move(self):
        index = None

        if len(self.MoveList) < 2:
            print("\nGetNextMove: Both players need to make at least one move")

        # Set the current position to the opponent's last move
        current_position = self.MoveList[-2]
        playerColor = self.CellNodesFeatureList[current_position]

        print(f"Current Position: {current_position} for {playerColor} ")

        index = self.evaluate_bridge()

        self.store_bp_index(index)

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





    #This function evaluates all the detected bridges and chooses the best one for the specified color

    def evaluate_bridge(self):

        index = None

        current_position = self.MoveList[-2]

        self.detect_bridge(current_position)
        bridge_patterns = self.PossibleBridgesList[current_position]

        print(f"Bridge Patterns for {current_position}: {bridge_patterns}")

        if bridge_patterns:
            if self.CellNodesFeatureList[current_position] == "Red":

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
            print(f"Appending {index} to Red_Bp at position")  # Debug statement
            self.Red_Bp.append(index)
            print("Complete Red_Bp:", self.Red_Bp)  # Shows the entire Red_Bp structure


        if playerColor == "Blue":
            print(f"Blue selected index: {index}")
            print(f"Appending {index} to Red_Bp at position")  # Debug statement
            self.Blue_Bp.append(index)
            print("Complete Red_Bp:", self.Blue_Bp)  # Shows the entire Red_Bp structure


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

        # Check if most upper bridge pattern is possible
        if index >= 2 * board_size:
            # the two row above index & the above and above-right index
            bp_top_index = (index - 2 * self.board_size + 1)
            top_r_index = (index - self.board_size + 1)
            top_l_index = (index - self.board_size)

            if (0 <= bp_top_index < len(self.CellNodesFeatureList) and
                    0 <= top_r_index < len(self.CellNodesFeatureList) and
                    0 <= top_l_index < len(self.CellNodesFeatureList) and
                    index % self.board_size != (self.board_size - 1) and
                    index % self.board_size != (self.board_size + 1)):

                # if all the cells needed for bridge pattern for current index is empty, the hex index to make the bridge pattern is appended in a list
                if self.CellNodesFeatureList[bp_top_index] == "None" and self.CellNodesFeatureList[
                    top_r_index] == "None" and self.CellNodesFeatureList[top_l_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_index)
                    # self.PossibleBridgesList.append(top_r_index)
                    # self.PossibleBridgesList.append(top_l_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_index)
                    """


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
                    # self.PossibleBridgesList.append(up_l_index)
                    # self.PossibleBridgesList.append(up_r_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_right_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_right_index)
                    """

        # Check if upper left bridge pattern is possible
        if index >= board_size and index % self.board_size != 0:
            bp_top_left_index = (index - self.board_size - 1)
            up_l_up_index = (index - self.board_size)
            up_l_down_index = (index - 1)

            if (0 <= bp_top_left_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_up_index < len(self.CellNodesFeatureList) and
                    0 <= up_l_down_index < len(self.CellNodesFeatureList)):  # Ensure not at right edge

                if self.CellNodesFeatureList[bp_top_left_index] == "None" and self.CellNodesFeatureList[
                    up_l_up_index] == "None" and self.CellNodesFeatureList[up_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_top_left_index)
                    # self.PossibleBridgesList.append(up_l_up_index)
                    # self.PossibleBridgesList.append(up_l_down_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_left_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_left_index)
                    """

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
                    # self.PossibleBridgesList.append(bot_l_index)
                    # self.PossibleBridgesList.append(bot_r_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_index)
                    """

        # Check if down right bridge pattern is possible
        if index < self.board_size * (self.board_size - 1) and index % self.board_size != (self.board_size - 1):
            bp_bot_right_index = (index + self.board_size + 1)
            bot_l_index = (index + self.board_size)
            bot_r_index = (index + 1)

            if (0 <= bp_bot_right_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_index < len(self.CellNodesFeatureList) and
                    0 <= bot_r_index < len(self.CellNodesFeatureList) and
                    index % self.board_size != (self.board_size + 2)):

                if self.CellNodesFeatureList[bp_bot_right_index] == "None" and self.CellNodesFeatureList[
                    bot_l_index] == "None" and self.CellNodesFeatureList[bot_r_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_right_index)
                    # self.PossibleBridgesList.append(bot_l_index)
                    # self.PossibleBridgesList.append(bot_r_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_right_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_right_index)
                    """

        # Check if down left bridge pattern is possible
        if index < self.board_size * (self.board_size - 1) and index % self.board_size > 1:
            bp_bot_left_index = (index + self.board_size - 2)
            bot_l_down_index = (index + self.board_size - 1)
            bot_l_up_index = (index - 1)

            if (0 <= bp_bot_left_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_up_index < len(self.CellNodesFeatureList) and
                    0 <= bot_l_down_index < len(self.CellNodesFeatureList)):

                if self.CellNodesFeatureList[bp_bot_left_index] == "None" and self.CellNodesFeatureList[
                    bot_l_up_index] == "None" and self.CellNodesFeatureList[bot_l_down_index] == "None":
                    self.PossibleBridgesList[index].append(bp_bot_left_index)
                    # self.PossibleBridgesList.append(bot_l_up_index)
                    # self.PossibleBridgesList.append(bot_l_down_index)
                    """
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_left_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_left_index)
                    """








