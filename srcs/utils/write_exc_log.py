import os
import datetime
import traceback

def write_exc_log_to_file(directory, category="exception"):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Get the current date and time as a string
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Generate the filename with the timestamp
    filename = os.path.join(directory, f"{category}_{timestamp}.log")

    # Write the traceback to the file
    with open(filename, "w") as log_file:
        traceback.print_exc(file=log_file)

    traceback.print_exc()
    print(f"\n\nException traceback written to {filename}\n")