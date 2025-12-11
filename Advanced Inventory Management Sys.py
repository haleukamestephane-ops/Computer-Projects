import csv
from colorama import Fore, Back, Style, init
import os

init(autoreset=True)  # Auto-reset after each print


def load_csv_files():
    
    folder = input(Style.BRIGHT + "\nEnter the name/path of the folder to open: ").lower()
    try:
        for filename in os.listdir(folder):

#Checking only for files having the extension .csv     
                if filename.endswith('.csv'):
                    file_path = os.path.join(folder, filename)       

#Loading the csv files 
                    print(Back.MAGENTA + Back.BLUE + Style.BRIGHT + f"\n📂 opening file: {filename}\n")
                    with open(file_path, 'r', encoding="utf-8-sig") as filename:
                        reader = csv.DictReader(filename)
                        for row in reader:
                            print(row)

#Handling errors

    except FileNotFoundError:
        if folder not in os.listdir("C:/Users/FUJITSU/OneDrive/Desktop"):
            print(f"❌❌ {folder} folder not found in any directory")
            load_csv_files()        
    except Exception as e:
        print(f"Unexpected error !")
        load_csv_files()

load_csv_files()