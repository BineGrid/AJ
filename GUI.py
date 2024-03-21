from Shift import Shift, load_shift_file, save_shift_file
import time
import json
import os
import Web
import DevLogger as DL
import DevReadWrite as DRW

try:
    import PySimpleGUI as sg
except ImportError as e:
    sg = None
    DL.logger.critical("PySimpleGUI doesn't seem to be installed. Please install it using 'pip install PySimpleGUI'.")
    DL.logger.critical("Exception: ", e)

with open('config.json') as f:
  config = json.load(f)
       
# Define the input layout of the GUI
input_layout = [
    [sg.Text("Select the CSV folder and Excel folder"), sg.Push(), sg.Button("Open Config")],
    [sg.Text("Please be sure to unzip the files!"), sg.Push(), sg.Checkbox("Delete Temp Files", key='delete')],
    [sg.Button('Open Chrome Tabs', key="-WEB-"),sg.Push(),sg.Checkbox("Save Reports", key='save')],
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

# Create the window
window = sg.Window("AutoJustin V2", input_layout, finalize=True, icon='AJ.ico')
curr_shift = None
csv_arr = []

# Load in default checkbox value from config
sales_labor_path = config["last_excel_path"]
download_path = config["download_dir"]

window["save"].update(config["save_reports"])
window["delete"].update(config["delete_temp_files"])

try:
# Event loop
    while True:
        event, values = window.read()
        
        if event == "-WEB-":
            Web.switch_tab_url(Web.Tabs.TOAST, config["TOASTHOME_URL"])
            Web.switch_tab_url(Web.Tabs.TOAST, config["TOASTSALES_URL"])
            Web.switch_tab_url(Web.Tabs.SHIFTNOTE, config["SHIFTREPORT_URL"])
        
        if event == "-LOAD-":
            load_path = sg.popup_get_file('Pick a saved shift to load', initial_folder=config["saved_reports_dir"], file_types=[("Shift Files","*.shift")])
            loaded_shift = load_shift_file(load_path)
            DL.logger.info("\n\n   - Loading Report -")
            
            # print loaded shift
            loaded_shift.print_member_variables()
            print(loaded_shift.get_hourly_report_str())
            print(loaded_shift.get_sales_proj_vs_act_perc())
            print(loaded_shift.get_sales_proj_vs_act_labor())
            print(loaded_shift.get_present_job_title_count())
        
        if event == "Open Config":
            os.startfile("config.json")
            
        if event == "Generate Report" and values["-DLFOLDER_TEXT-"] and values["-EXCELFOLDER_TEXT-"]:
            DL.logger.info("\n   - Generating Report -")
            config["download_dir"] = download_dir = values["-DLFOLDER_TEXT-"]  # Use -CSVFOLDER_TEXT- to get the value
            config["last_excel_path"] = sales_labor_path = values["-EXCELFOLDER_TEXT-"]  # Use -EXCELFOLDER_TEXT- to get the value
            config["save_reports"] = values["save"]
            config["delete_temp_files"] = values["delete"]
            DRW.write_config(config)
        
            try:
                encapsulated_data = DRW.create_ecapsulated_data(config["temp_dir"], sales_labor_path)
                curr_shift = Shift(encapsulated_data)
            except Exception as e:
                DL.logger.error("ERROR: Failed to read CSV files")
                DL.logger.exception(e)
                
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
                
            #Web.ShiftNote.enter_shift(Web.ShiftNote, curr_shift)
                
        elif event == "Generate Report":
            DL.logger.error("ERROR: Missing required file path(s)!")

        if event == sg.WIN_CLOSED:
            config["download_dir"] = download_path = values["-DLFOLDER_TEXT-"]  # Use -CSVFOLDER_TEXT- to get the value
            config["last_excel_path"] = sales_labor_path = values["-EXCELFOLDER_TEXT-"]  # Use -EXCELFOLDER_TEXT- to get the value
            config["save_reports"] = values["save"]
            config["delete_temp_files"] = values["delete"]
            DRW.write_config(config)
            
except Exception as e:
    DL.logger.exception(e)
    DL.logger.critical("-= Closing window in 20 seconds! =-")
    time.sleep(20)

# Close the window
window.close()
