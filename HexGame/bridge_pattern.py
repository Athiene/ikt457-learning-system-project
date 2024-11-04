
class BP:


    def __init__(self, size, cell_node_feature_list, cell_nodes_edge_list, move_list):
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

        self.Red_Bp = [[] for _ in range(self.board_size * self.board_size)]

        self.Blue_Bp = [[] for _ in range(self.board_size * self.board_size)]

        return

    def get_next_move(self):
        index = None

        if len(self.MoveList) < 2:
            print("\nGetNextMove: Both players need to make at least one move")



        # Set the current position to the opponent's last move
        current_position = self.MoveList[-2]

        print(f"Current Position: {current_position}")

        # Step 1: Detect possible bridges for the current position
        self.detect_bridge(current_position)

        # Step 2: Find the highest index from detected bridges
        bridge_patterns = self.PossibleBridgesList[current_position]

        print(f"Bridge Patterns for {current_position}: {bridge_patterns}")

        if bridge_patterns:
            # Find and set the highest index from the list of possible bridges
            index = max(bridge_patterns)

        # Return the highest index as the next move, or None if no bridges are available
        return index



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



    def evalute_bridge(self, index):
        current_position = self.MoveList[-2]
        bridge_patterns = self.PossibleBridgesList[current_position]

        best_score = 0

        for bridge in bridge_patterns:
            score = 0

            # Criterion 1: Proximity to Walls based on player color
            if self.is_near_wall(bridge):
                score += 10  # Arbitrary score for being near a wall


            if score > best_score:
                best_score = score

        return None





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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_index)


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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_right_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_right_index)

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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_top_left_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_top_left_index)

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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_index)

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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_right_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_right_index)

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
                    if playerColor == "Red":
                        self.Red_Bp[index].append(bp_bot_left_index)
                    elif playerColor == "Blue":
                        self.Blue_Bp[index].append(bp_bot_left_index)





