import os
import pandas as pd

# Get current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct relative path to the CSV
csv_path = os.path.join(current_dir, "../data/adidas.csv")

# Read the CSV file
df = pd.read_csv(csv_path)

# Display the first few rows
print(df.head())
