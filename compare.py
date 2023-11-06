import sqlite3
# Define the database connection
conn = sqlite3.connect('requirements.db')
cursor = conn.cursor()

# Define a function to fetch and print a sample of the data
def fetch_sample_data(cursor, table_name, sample_size=5):
    # Execute the SELECT query
    cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (sample_size,))
    
    # Fetch the results
    rows = cursor.fetchall()
    
    # Print out the sample data
    for row in rows:
        print(row)

# Fetch and print a sample from the requirements table
try:
    fetch_sample_data(cursor, 'requirements')
except Exception as e:
    print("An error occurred while fetching data:", e)
finally:
    # Close the database connection
    conn.close()