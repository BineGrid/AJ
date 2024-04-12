from DevData import DCDictionary
from Shift import Shift, load_shift_file, save_shift_file
import time
import json
import os
import Web
import DevLogger as DL
import DevReadWrite as DRW
import time

try:
    import PySimpleGUI as sg
except ImportError as e:
    sg = None
    DL.logger.critical("PySimpleGUI doesn't seem to be installed. Please install it using 'pip install PySimpleGUI'.")
    DL.logger.critical("Exception: ", e)

with open('config.json') as f:
  config = json.load(f)
  
  
#██╗      █████╗ ██╗   ██╗ ██████╗ ██╗   ██╗████████╗███████╗
#██║     ██╔══██╗╚██╗ ██╔╝██╔═══██╗██║   ██║╚══██╔══╝██╔════╝
#██║     ███████║ ╚████╔╝ ██║   ██║██║   ██║   ██║   ███████╗
#██║     ██╔══██║  ╚██╔╝  ██║   ██║██║   ██║   ██║   ╚════██║
#███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝   ██║   ███████║
#╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝

# Define the input layout of the GUI
input_layout = [
    [sg.Text("Select the Dowloads folder and Excel folder"), sg.Push(), sg.Button('⚙ Settings', size=(10, 1),  enable_events=True, font=('Arial', 12))],
    [sg.Checkbox("Delete Temp Files", key='delete'), sg.Push()],
    [sg.Checkbox("Save Reports", key='save'),sg.Push(),sg.Button('Payroll Tool', key="-PAY-")],
    [
        sg.FolderBrowse(button_text="Dwnld Folder", enable_events=True, size=(10, 2)),
        sg.InputText(config["download_dir"], key="-DLFOLDER_TEXT-", size=(98, 1)),
    ],
    [
        sg.FileBrowse(button_text="S&L File", enable_events=True, size=(10, 2)),
        sg.InputText(config["last_excel_path"], key="-EXCELFOLDER_TEXT-", size=(98, 1)),
    ],
    [
        sg.Button("Generate Report", size=(15, 3)), sg.Push(), 
        sg.Button(button_text="Load Old Report", size=(12, 2), key="-LOAD-")
    ],
    [sg.Output(size=(110, 25), key="-OUTPUT-")]
]

# ██████╗ ██╗   ██╗██╗    ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗███████╗
#██╔════╝ ██║   ██║██║    ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║██╔════╝
#██║  ███╗██║   ██║██║    ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║███████╗
#██║   ██║██║   ██║██║    ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║╚════██║
#╚██████╔╝╚██████╔╝██║    ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝███████║
# ╚═════╝  ╚═════╝ ╚═╝     ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝

# Create the window
window = sg.Window("AutoJustin V2", input_layout, finalize=True, icon='AJ.ico')
curr_shift = None
csv_arr = []

# Load in default checkbox value from config
sales_labor_path = config["last_excel_path"]
download_path = config["download_dir"]

# Update the gui elements with the old values from the config
window["save"].update(config["save_reports"])
window["delete"].update(config["delete_temp_files"])

def openSettings():
    layout = [
        [sg.Text('Color Scheme:')],
        [sg.Listbox(sg.theme_list(), default_values=[sg.user_settings_get_entry('theme')], size=(15, 8), k='ThemeListBox')],
        [sg.VPush()],
        [sg.Button('Cancel'), sg.Button('Save'), sg.Push()]]
    
    # Create the Window
    window = sg.Window('Settings', layout,
                        size=(500, 500), icon='AJ.ico')


# ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
#██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
#██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
#██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
#╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
# ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
#          ██╗      ██████╗  ██████╗ ██████╗                  
#          ██║     ██╔═══██╗██╔═══██╗██╔══██╗                 
#          ██║     ██║   ██║██║   ██║██████╔╝                 
#          ██║     ██║   ██║██║   ██║██╔═══╝                  
#          ███████╗╚██████╔╝╚██████╔╝██║                      
#          ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝                      

try:
# Event loop
    while True:
        event, values = window.read()
        
        if event == "-LOAD-":
            start_time = time.process_time()
            DL.logger.info("\n\n   - Loading Report -")
            # Find the .shift file and load it in as a Shift class
            load_path = sg.popup_get_file('Pick a saved shift to load', initial_folder=config["saved_reports_dir"], file_types=[("Shift Files","*.shift")])
            loaded_shift = load_shift_file(load_path)
            
            # print loaded shift
            # This allows for older shift files to still be backwards compatible
            updated_shift = Shift(DCDictionary(loaded_shift.encaped_data.Ndfs_arr))
            print(updated_shift.get_hourly_report_str())
            print(updated_shift.get_sales_proj_vs_act_perc())
            print(updated_shift.get_sales_proj_vs_act_labor())
            print(updated_shift.get_present_job_title_count())
            
            load_time = time.process_time()
            DL.logger.debug(f"[LOAD Time]: {(load_time - start_time):0.4f}s")
        
        # Literally opens the config.json lol
        if event == "Open Config":
            os.startfile("config.json")
            
        if event == "Generate Report" and values["-DLFOLDER_TEXT-"] and values["-EXCELFOLDER_TEXT-"]:
            start_time = time.process_time()
            
            # Update all the settings and file paths from the gui elements to the config
            DL.logger.info("\n   - Generating Report -")
            config["download_dir"] = download_dir = values["-DLFOLDER_TEXT-"]
            config["last_excel_path"] = sales_labor_path = values["-EXCELFOLDER_TEXT-"]
            config["save_reports"] = values["save"]
            config["delete_temp_files"] = values["delete"]
            DRW.write_config(config)
            
            # Log Config Read Write Time
            config_time = time.process_time()
            DL.logger.debug(f"[Config RW Time]: {(config_time - start_time):0.4f}s")

            # Download all the files from the web then move it to /temp
            try: 
                Web.init_chrome()
                Web.Toast.download_sales_summary()
                DRW.unzip_sales_summary(config["download_dir"])
                Web.Toast.download_payroll_export()
                DRW.rellocate_payroll_csv(config["download_dir"])
            except Exception as e:
                DL.logger.critical("ERROR: Failed to download the csv files from toast!")
                DL.logger.exception(e)
            
            download_csv_time = time.process_time()
            DL.logger.debug(f"[Download CSV Time]: {(download_csv_time - config_time):0.4f}s")
        
            # Convert all the needed csv files in temp to a DCArray
            # Then create a Shift object with it
            try:
                encapsulated_data = DRW.create_ecapsulated_data(config["temp_dir"], sales_labor_path)
                
                encapsulated_time = time.process_time()
                DL.logger.debug(f"[Data Encapsulation Time]: {(encapsulated_time - download_csv_time):0.4f}s")
                
                curr_shift = Shift(encapsulated_data)
                
                encapsulated_read_time = time.process_time()
                DL.logger.debug(f"[Encaped Data Read Time]: {(encapsulated_read_time - encapsulated_time):0.4f}s")
                
                # Delete all files in temp if config says so
                if config["delete_temp_files"]:
                    DRW.delete_everything_in_dir(config["temp_dir"])
                    
            except Exception as e:
                DL.logger.error("ERROR: Failed to read CSV files")
                DL.logger.exception(e)

            # Enter all the info into Shiftnote
            try:
                Web.ShiftNote.enter_shift(Web.ShiftNote, curr_shift)
            except Exception as e:
                DL.logger.error("ERROR: Failed to input shift into ShiftNote")
                DL.logger.exception(e)
                
            shiftnote_time = time.process_time()
            DL.logger.debug(f"[Enter ShiftNote Time]: {(shiftnote_time - encapsulated_read_time):0.4f}s")
                
            
            # Print all the data because its cool
            try:
                curr_shift.print_member_variables()
                print(curr_shift.get_hourly_report_str())
                print(curr_shift.get_sales_proj_vs_act_perc())
                print(curr_shift.get_sales_proj_vs_act_labor())
                print(curr_shift.get_present_job_title_count())
                
                if config['save_reports']:
                    save_shift_file(curr_shift)
                
            except Exception as e:
                DL.logger.error("ERROR: Failed to print shift details! Exception:")
                DL.logger.exception(e)
                
            data_out_time = time.process_time()
            DL.logger.debug(f"[Print and Save Time]: {(data_out_time - shiftnote_time):0.4f}s")
                
        elif event == "Generate Report":
            DL.logger.error("ERROR: Missing required file path(s)!")

        # Update all the settings and file paths from the gui elements to the config
        # When the window closes
        if event == sg.WIN_CLOSED:
            config["download_dir"] = values["-DLFOLDER_TEXT-"]
            config["last_excel_path"] = values["-EXCELFOLDER_TEXT-"]
            config["save_reports"] = values["save"]
            config["delete_temp_files"] = values["delete"]
            DRW.write_config(config)
            break
            
# Just catch any possible exception that way the gui doesn't just suddenly close
except Exception as e:
    DL.logger.exception(e)
    DL.logger.critical("-= Closing window in 20 seconds! =-")
    time.sleep(2)

# Close the window just in case it gets stuck somehow
window.close()
