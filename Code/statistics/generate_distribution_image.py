import matplotlib.pyplot as plt
from collections import Counter

def read_file_counts(file_path):
    """
    Reads the file counts and repository names from a text file.
    Args:
        file_path (str): Path to the input file.
    Returns:
        list: A list of file counts (integers).
    """
    file_counts = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                # Split the line into file count and repository name
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    file_count = int(parts[0])  # Convert file count to integer
                    file_counts.append(file_count)
    except Exception as e:
        print(f"Error reading file: {e}")
    return file_counts

def plot_file_distribution_bar_chart(file_counts, output_image):
    """
    Plots a bar chart of file counts across repositories.
    Args:
        file_counts (list): A list of file counts (integers).
        output_image (str): Path to save the output image.
    """
    # Count the number of repositories for each unique file count
    count_distribution = Counter(file_counts)

    # Sort the data by file count
    sorted_counts = sorted(count_distribution.items())

    # Extract data for the bar chart
    x_labels = [str(file_count) for file_count, _ in sorted_counts]
    y_values = [repo_count for _, repo_count in sorted_counts]

    # Create the bar chart
    plt.figure(figsize=(30, 10))  # Increase figure size for better readability
    bar_width = 0.8  # Adjust bar width based on number of bars
    plt.bar(x_labels, y_values, color="skyblue", edgecolor="black", width=bar_width)

    # Adjust X-axis labels for readability
    plt.xticks(range(len(x_labels)), x_labels, rotation=45, ha="right", fontsize=6)  # Smaller font size

    # Add labels and title
    plt.xlabel("Number of Files", fontsize=14)
    plt.ylabel("Number of Repositories", fontsize=14)
    plt.title("Distribution of File Counts Across Repositories", fontsize=16)
    plt.tight_layout()

    # Save the image
    plt.savefig(output_image, dpi=300)
    print(f"Bar chart image saved as {output_image}")

    # Show the plot (optional)
    plt.show()

def main():
    """
    Main function to read data and generate the bar chart.
    """
    # Path to the input file
    input_file = "count_files_per_repo_output.txt"
    
    # Output image path
    output_image = "file_distribution_bar_chart_no_bins.png"
    
    # Read the file counts from the file
    file_counts = read_file_counts(input_file)
    
    # Check if data was successfully read
    if file_counts:
        # Call the function to plot the bar chart
        plot_file_distribution_bar_chart(file_counts, output_image)
    else:
        print("No data to plot. Please check the input file.")

# Call the main function
if __name__ == "__main__":
    main()
