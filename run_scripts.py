import subprocess

def run_script(script_name):
    try:
        # Run the given script as a subprocess
        result = subprocess.run(['python', script_name], check=True, text=True, capture_output=True)
        print(f"Output of {script_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}:\n{e.stderr}")

def main():
    # Ask the user whether to run data_download.py and then tracker.py or just tracker.py
    choice = input("Enter 1 to run data_download.py then tracker.py, or 0 to run only tracker.py: ").strip()

    if choice == '1':
        print("Running data_download.py...")
        run_script('data_download.py')  # Run data_download.py
        print("Running tracker.py...")
        run_script('tracker.py')         # Run tracker.py
    elif choice == '0':
        print("Running tracker.py...")
        run_script('tracker.py')         # Run tracker.py only
    else:
        print("Invalid input. Please enter 1 or 0.")

if __name__ == "__main__":
    main()
