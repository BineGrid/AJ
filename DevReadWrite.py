import json
import os
from pathlib import Path
import DevLogger as DL
import DevData as DD

try:
    import pandas as pd
except ImportError as e:
    pd = None
    DL.logger.critical("Pandas doesn't seem to be installed. Please install it using 'pip install pandas'.")
    DL.logger.critical("Exception: ", e)

with open('config.json') as f:
  config = json.load(f)

def write_config(conf):
    '''
        This updates the config with its new values
    '''
    with open('config.json', 'w') as f:
        json.dump(conf, f, indent=4)
        
def __process_files_into_Ndf_arr(csv_path, excel_path):
    '''
        This returns an NamedDataFrame array
    '''
    result_Ndf_arr = []
    files_found = 0
    
    # --= Get file paths from config =-- #
    files_to_read = config.get("csv_files_to_encapsulate", [])
    payroll_CSV_name = config["payroll_CSV_name"]

    for filename in os.listdir(csv_path):
        if filename in files_to_read:
            file_path = os.path.join(csv_path, filename)
            df = pd.read_csv(file_path)

            # Adds the content to the NDF_Arr
            result_Ndf_arr.append(DD.NamedDataFrame(file_path, df))
            files_found += 1
            
        # This adds the all labor info to the NDF_Arr
        elif filename.startswith(payroll_CSV_name):
            file_path = os.path.join(csv_path, filename)
            result_Ndf_arr.append(DD.NamedDataFrame(file_path, pd.read_csv(os.path.join(csv_path, filename))))
            files_found += 1

    for filename in os.listdir(excel_path):
        if filename.startswith("S&L"):
            for sheet in ("S&L", "BoH Schedule", "FoH Schedule"):
                file_path = os.path.join(excel_path, filename)
                df = pd.read_excel(file_path, sheet_name=sheet)
                # Adds the content to the NDF_Arr
                result_Ndf_arr.append(DD.NamedDataFrame(file_path, df))
                files_found += 1 

    # + 3 for the 3 sheets in the excel S&L file
    if files_found == len(files_to_read) + 4: 
        DL.logger.info("All Files Successfully Found!")
    elif files_found == 0:
        DL.logger.error("ERROR: No files found!")
    else:
        DL.logger.error(f"ERROR: {(len(files_to_read) + 4) - files_found} file(s) missing!")

    return result_Ndf_arr

def create_ecapsulated_data(csv_folder_path, excel_folder_path) -> DD.DCArray:
    try:
        DL.logger.debug("Starting Data Encapsulation")
        encapsulated_data = DD.DCArray(__process_files_into_Ndf_arr(csv_folder_path, excel_folder_path))
        DL.logger.debug(f"Encapsulated Data: {encapsulated_data.size()}")
    except Exception as e:
        DL.logger.error("ERROR: Failed to process CSV files. Exception:", e)
        
    return encapsulated_data

def get_newest_file(dir: str):
    return sorted(Path(dir).iterdir(), key=os.path.getmtime)[-1]

def unzip_sales_summary(dir: str):
    last_download = get_newest_file(dir)
    if(last_download.startswith(config["sales_summary_name"])):
        pass
    else:
        DL.logger.error(f"ERROR: No CSV files found in dir: {dir}")
    print(last_download)
    
unzip_sales_summary(config["download_dir"])
                        
            




