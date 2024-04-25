import Config
import os
from pathlib import Path
import zipfile
import DevLogger as DL
import DevData as DD
import openpyxl
from Shift import Shift

try:
    import pandas as pd
except ImportError as e:
    pd = None
    DL.logger.critical("Pandas doesn't seem to be installed. Please install it using 'pip install pandas'.")
    DL.logger.critical("Exception: ", e)

config = Config.get_config()

def find_full_sl_path(dir: str):
    for file_name in os.listdir(dir):
        if file_name.startswith("S&L"):
            return os.path.join(dir, file_name)
        
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
    
    full_sl_path = find_full_sl_path(config["temp_dir"])

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
        
def write_shift_into_sl(shift: Shift):
    '''
        Takes in the shift object and writes it to the S&L file within the shift object
    '''
    
    # Pass the real reference to the shift object
    DCDict: DD.DCDictionary = shift.encaped_data
    
    # Get the currDay string
    currDay = shift.currDay
    today = ''
    
    # Convert Toast Currday to the S&L style days
    match(currDay):
        case 'Mon':
            today = "Monday"
        case 'Tue':
            today = "Tuesday"
        case 'Wed':
            today = "Wednesday"
        case 'Thu':
            today = "Thursday"
        case 'Fri':
            today = "Friday"
        case 'Sat':
            today = "Saturday"
        case 'Sun':
            today = "Sunday"
        
    # write everything to the local S&L file
    DCDict[f"S&L-SALES Bar/DR/Patio-{today}"].write((shift.netSales - shift.takeoutSales))
    DCDict[f"S&L-SalesTakeout/Delivery-{today}"].write((shift.takeoutSales))
    DCDict[f"S&L-Actual Daily Kitchen Hrs-{today}"].write((shift.ActBOHHours))
    DCDict[f"S&L-Actual Daily Dining Room Hrs-{today}"].write((shift.ActFOHHours))
    DCDict[f"S&L-Actual Daily Labor $ BOH-{today}"].write((shift.ActBOHLabor))
    DCDict[f"S&L-Actual Daily Labor $ FOH-{today}"].write((shift.ActFOHLabor))
    DCDict[f"S&L-Grubhub-{today}"].write((shift.grubhubSales))
    DCDict[f"S&L-Doordash-{today}"].write((shift.doordashSales))
    #DCDict[f"S&L-Total SP $-{today}"].write((shift.totalDiscounts))
    
    
    
    

                        
            




