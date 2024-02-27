import csv

# Path to your CSV file
csv_file_path = 'mcplant_locations_feb_2024.csv'

# Initialize an empty list to hold the CSV data
data_array = []

# Open the CSV file for reading
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Loop through each row in the CSV file
    for row in csv_reader:
        # Append the current row to our data array
        data_array.append(row)

# Print the array to see the contents
for row in data_array:
    print(row)
