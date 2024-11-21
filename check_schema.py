import sqlite3

def fetch_all_data_from_table(db_path, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Execute SELECT statement to fetch all rows and columns from the table
    query = f"SELECT * FROM {table_name} LIMIT 3;"
    cursor.execute(query)
    
    # Fetch all rows of the table
    rows = cursor.fetchall()
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    # Print column names
    print(f"Data from table '{table_name}':")
    print(" | ".join(columns))  # Print column names
    
    # Print each row of the table
    for row in rows:
        print(" | ".join(str(value) for value in row))  # Print each row

    # Close the connection
    conn.close()

# Path to your SQLite database
db_path = 'ticker_data.db'

# Table name you want to fetch data from
table_name = 'XBI'

# Fetch and display all data from the table
fetch_all_data_from_table(db_path, table_name)
