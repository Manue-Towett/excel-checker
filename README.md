# excel-checker
Removes blaclisted and duplicated domains from excel files

# Requires
- python 3.11+

# Settings
- There are two configuration files:
    - settings:
        - use this to set:
            - input - the folder where the input excel files are located
            - output - the folder where the processed files will go to
            - master - the folder where the master excel which tracks domains to eliminate duplicates will go to
            - processed_files - the folder where the text file which tracks files processed will be saved to
    
    - blacklisted:
        - write blacklisted domains in this file, each on its own line with no empty lines

# Usage
- Open the command prompt / terminal
- cd into the project folder / directory
- If running for the first time, first install dependencies using the command: 
    ```pip install -r requirements.txt```
- To run the script, use the commands:
    - For Linux/MacOS: 
        ```python3 main.py```
    - For windows: 
        ```python main.py```