# import sqlite3

# def check_table_schema(db_path, table_name):
#     # Connect to the SQLite database
#     conn = sqlite3.connect(db_path)
    
#     # Create a cursor object
#     cursor = conn.cursor()
    
#     # Execute PRAGMA statement to fetch table schema
#     query = f"PRAGMA table_info({table_name});"
#     cursor.execute(query)
    
#     # Fetch the results
#     columns = cursor.fetchall()
    
#     # Print the column details
#     print(f"Schema for table '{table_name}':")
#     for column in columns:
#         # Each column is a tuple (cid, name, type, notnull, dflt_value, pk)
#         print(f"Column: {column[1]} | Type: {column[2]} | Not Null: {column[3]} | Default: {column[4]} | Primary Key: {column[5]}")
    
#     # Close the connection
#     conn.close()

# # Path to your SQLite database
# db_path = 'ticker_data.db'

# # Table name you want to inspect
# table_name = 'XBI'

# # Check schema of the table
# check_table_schema(db_path, table_name)


import sqlite3

def fetch_all_data_from_table(db_path, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Execute SELECT statement to fetch all rows and columns from the table
    query = f"SELECT * FROM {table_name};"
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
