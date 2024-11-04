import matplotlib.pyplot as plt
import os

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


def double_plot(values_1, values_2, title_name, x_label, y_label, labels, file_name):
    # Get the current directory where the function is called
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)
    
    # Check if the file already exists and prompt the user for deletion
    if os.path.isfile(file_name+".png"):
        response = input(f"The file '{file_name}' already exists. Do you want to delete it? (y/n): ").strip().lower()
        if response == 'y' or response=='yes':
            os.remove(file_name+".png")
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
    plt.legend()
    
    # Save the plot to the specified path as a PNG file
    plt.savefig(file_path)
    plt.close()
    
    return file_path
