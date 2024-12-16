import matplotlib.pyplot as plt
import os
import numpy as np

def single_plot(values, title_name, x_label, y_label, file_name):
    # Get the current directory where the function is called
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)
    
    # Check if the file already exists and prompt the user for deletion
    if os.path.isfile(file_name+".png"):
        response = input(f"The file '{file_name}' already exists. Do you want to delete it? (y/n): ").strip().lower()
        if response == 'y' or response == 'yes':
            os.remove(file_name+".png")
            print(f"Deleted existing file '{file_name}'.")
        else:
            print("File not deleted. Exiting function without saving.")
            return None
    
    # Plotting the values
    plt.figure()
    plt.plot(values, marker='o')
    plt.title(title_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    # Save the plot to the specified path as a PNG file
    plt.savefig(file_path)
    plt.close()
    
    return file_path


def double_plot(values_1, values_2, title_name, x_label, y_label, labels, file_name, kvalue1=None, kvalue2=None):
    # Get the current directory where the function is called
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)
    
    # Check if the file already exists and prompt the user for deletion
    if os.path.isfile(file_name + ".png"):
        response = input(f"The file '{file_name}' already exists. Do you want to delete it? (y/n): ").strip().lower()
        if response == 'y' or response == 'yes':
            os.remove(file_name + ".png")
            print(f"Deleted existing file '{file_name}'.")
        else:
            print("File not deleted. Exiting function without saving.")
            return None
    
    # Plotting two sets of values on the same graph
    plt.figure()
    plt.plot(values_1, marker='o', label=labels[0])
    plt.plot(values_2, marker='s', label=labels[1])
    plt.title(title_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    # Adding horizontal lines and annotations for averages if provided
    if kvalue1 is not None:
        plt.axhline(y=kvalue1, color='blue', linestyle='--', linewidth=0.8, label=f"Avg {labels[0]}: {kvalue1:.2f}")
        # Position the text just to the right of the last point to ensure it is visible
        #plt.text(len(values_1) - 0.5, kvalue1, f"{kvalue1:.2f}", va='center', ha='left', color='black', fontweight='bold')
    
    if kvalue2 is not None:
        plt.axhline(y=kvalue2, color='orange', linestyle='--', linewidth=0.8, label=f"Avg {labels[1]}: {kvalue2:.2f}")
        # Position the text just to the right of the last point to ensure it is visible
        #plt.text(len(values_2) - 0.5, kvalue2, f"{kvalue2:.2f}", va='center', ha='left', color='black', fontweight='bold')
    
    # Display the combined legend for both plot lines and average lines
    plt.legend()
    
    # Save the plot to the specified path as a PNG file
    plt.savefig(file_path)
    plt.close()
    
    return file_path



def plot_moves_distribution(simulation_train, simulation_test, title_name, x_label, y_label, file_name):
    # Get the current directory where the function is called
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)

    print(f"LENGTH OF TRAIN DATA: {len(simulation_train)}")
    print(f"LENGTH OF TEST DATA: {len(simulation_test)}")

    # Count total moves in training data
    total_moves_train = []
    for game in simulation_train:
        moveCount = sum(1 for feature in game[1] if feature != "None")
        total_moves_train.append(moveCount)
    
    # Count total moves in testing data
    total_moves_test = []
    for game in simulation_test:
        moveCount = sum(1 for feature in game[1] if feature != "None")
        total_moves_test.append(moveCount)

    def create_intervals(data, max_bins=36, interval_size=3):
        """Create intervals if unique x-values exceed max_bins."""
        unique_values = sorted(set(data))
        if len(unique_values) > max_bins:
            min_val, max_val = min(data), max(data)
            bins = range(min_val, max_val + interval_size, interval_size)
            aggregated_data = np.histogram(data, bins=bins)[0]
            interval_labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins) - 1)]
            return aggregated_data, interval_labels
        return data, None  # No need for intervals

    # Check and aggregate intervals for train data
    train_data, train_labels = create_intervals(total_moves_train)

    # Check and aggregate intervals for test data
    test_data, test_labels = create_intervals(total_moves_test)

    # Plot the histograms
    plt.figure(figsize=(14, 6))

    # Training data histogram
    plt.subplot(1, 2, 1)
    if train_labels:
        plt.bar(range(len(train_labels)), train_data, tick_label=train_labels, edgecolor='black')
        plt.xticks(rotation=45)
    else:
        plt.hist(total_moves_train, bins=20, edgecolor='black')
    plt.title(f"{title_name} - Training Data")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.annotate(f"Total games: {len(total_moves_train)}", xy=(0.95, 0.95), xycoords='axes fraction', 
                 ha='right', va='top', fontsize=10, color='black', fontweight='bold')

    # Testing data histogram
    plt.subplot(1, 2, 2)
    if test_labels:
        plt.bar(range(len(test_labels)), test_data, tick_label=test_labels, edgecolor='black')
        plt.xticks(rotation=45)
    else:
        plt.hist(total_moves_test, bins=20, edgecolor='black')
    plt.title(f"{title_name} - Testing Data")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.annotate(f"Total games: {len(total_moves_test)}", xy=(0.95, 0.95), xycoords='axes fraction', 
                 ha='right', va='top', fontsize=10, color='black', fontweight='bold')

    # Save the plot to the specified path as a PNG file
    plt.tight_layout()  # Ensure layout fits well with rotated labels
    plt.savefig(file_path)
    plt.close()

    # Show the plot
    plt.show()

    return file_path
