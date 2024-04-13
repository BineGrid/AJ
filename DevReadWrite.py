import json
import os
from pathlib import Path
import zipfile
import DevLogger as DL
import DevData as DD
import openpyxl

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
        
def __process_files_into_Ndf_arr(csv_path, sl_path):
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
    
    for file_name in os.listdir(config["temp_dir"]):
        if file_name.startswith("S&L"):
            full_sl_path = os.path.join(sl_path, file_name)
            print(f"Full S&L Path: {full_sl_path}")

    xl_workbook = openpyxl.load_workbook(full_sl_path)
    for sheet in ("S&L", "BoH Schedule", "FoH Schedule"):
        df = pd.read_excel(full_sl_path, sheet_name=sheet)
        xl_sheet = xl_workbook[sheet]
        # Adds the content to the NDF_Arr
        result_Ndf_arr.append(DD.NamedDataFrame(full_sl_path, df, xl_sheet, xl_workbook))
        files_found += 1 

    # + 3 for the 3 sheets in the excel S&L file
    if files_found == len(files_to_read) + 4: 
        DL.logger.info("All Files Successfully Found!")
    elif files_found == 0:
        DL.logger.error("ERROR: No files found!")
    else:
        DL.logger.error(f"ERROR: {(len(files_to_read) + 4) - files_found} file(s) missing!")

    return result_Ndf_arr

def create_ecapsulated_data(csv_folder_path, excel_folder_path) -> DD.DCDictionary:
    try:
        DL.logger.debug("Starting Data Encapsulation")
        encapsulated_data = DD.DCDictionary(__process_files_into_Ndf_arr(csv_folder_path, excel_folder_path))
        DL.logger.debug(f"Encapsulated Data: {encapsulated_data.size()}")
    except Exception as e:
        DL.logger.error("ERROR: Failed to process CSV files. Exception:")
        DL.logger.exception(e)
        
    return encapsulated_data

def get_newest_file(dir: str) -> Path:
    '''
        Grabs the most recent file from a dir
    '''
    try:
        return sorted(Path(dir).iterdir(), key=os.path.getmtime)[-1]
    except Exception as e:
        DL.logger.critical("ERROR: Failed to grab newest file!")
        DL.logger.exception(e)
        return Path()

def rellocate_payroll_csv(dir: str, delete = config["delete_temp_files"]):
    '''
        This relloactes the payrollexport.csv to the temp dir
    '''
    last_download = get_newest_file(dir)
    file_path, filename = os.path.split(last_download)
    
    try:
        if filename.startswith(config["payroll_CSV_name"]):
            os.rename(last_download, os.path.join(config["temp_dir"], filename))
        else:
            DL.logger.error(f"ERROR: No Payroll CSV file found in dir: {dir}")
    except Exception as e:
        DL.logger.critical("ERROR: Failed to move PayrollExport...csv!")
        DL.logger.exception(e)

def unzip_sales_summary(dir: str, delete = config["delete_temp_files"]):
    last_download = get_newest_file(dir)
    file_path, filename = os.path.split(last_download)
    try:
        if(filename.startswith(config["sales_summary_name"])):
            with zipfile.ZipFile(last_download, 'r') as zip_ref:
                zip_ref.extractall(config["temp_dir"])
        
        # Delete download
        if delete:
            os.remove(os.path.join(config["download_dir"], last_download))
        else:    
            DL.logger.error(f"ERROR: No CSV files found in dir: {dir}")
        print("Last Download:", last_download)
        print("Filename:", filename)
    except Exception as e:
        DL.logger.critical("ERROR: Failed unzip CSV files!")
        DL.logger.exception(e)
        
def delete_everything_in_dir(dir: str):
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
    
#unzip_sales_summary(config["download_dir"])
#rellocate_payroll_csv(config["download_dir"])

                        
            




