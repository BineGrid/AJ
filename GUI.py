from tkinter.font import BOLD
from DevData import DCDictionary
import SugarSync
from datetime import date
from Shift import Shift, load_shift_file, save_shift_file
import time
import Config
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

config = Config.config

#███████╗████████╗ █████╗ ██████╗ ████████╗    ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗
#██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝    ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║
#███████╗   ██║   ███████║██████╔╝   ██║       ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║
#╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║
#███████║   ██║   ██║  ██║██║  ██║   ██║       ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝
#╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ 

def open_start_window():
    # Update the config to the latest values
    Config.read()
    
    sg.theme(config["theme"])
    
    start_layout = [
        [
            sg.Button('Payroll Buddy', key="-PAY-"), sg.Push(), sg.Text("Welcome to ", font=("Georgia", 20, 'bold')),
            sg.Text("AJ", font=("Impact", 28), text_color="gold"), sg.Push(), sg.Button("Config.json")
        ],
        [sg.Push(), sg.Text("Please select a tool", font=("Georgia", 14, 'bold')), sg.Push()],
        [sg.Button("Auto Closer", size=(12, 2)), sg.Push(), sg.Button("⚙ Settings", key="settings", size=(12, 2))]]
    
    window = sg.Window('Starting Window', start_layout, size=(950, 240), icon='AJ.ico')

    while True:
        event, values = window.read()
        
        if event == 'Auto Closer':
            window.close()
            open_input_window()
            break
            
        if event == 'settings':
            window.close()
            open_settings_window()
            break
        
        # Literally opens the config.json lol
        if event == "Config.json":
            os.startfile("config.json")
        
        # if user closes window
        if event == sg.WIN_CLOSED:
            Config.write()
            break
    
#███████╗███████╗████████╗████████╗██╗███╗   ██╗ ██████╗ ███████╗
#██╔════╝██╔════╝╚══██╔══╝╚══██╔══╝██║████╗  ██║██╔════╝ ██╔════╝
#███████╗█████╗     ██║      ██║   ██║██╔██╗ ██║██║  ███╗███████╗
#╚════██║██╔══╝     ██║      ██║   ██║██║╚██╗██║██║   ██║╚════██║
#███████║███████╗   ██║      ██║   ██║██║ ╚████║╚██████╔╝███████║
#╚══════╝╚══════╝   ╚═╝      ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
    
def open_settings_window():
    # Update the config to the latest values
    Config.read()
    
    settings_layout = [
        [sg.Push(), sg.Text("Window Settings", font=("Arial", 20)), sg.Push()],
        [sg.Text('Color Scheme:')],
        [sg.Listbox(sg.theme_list(), default_values=[sg.user_settings_get_entry('theme')], size=(15, 8), k='ThemeListBox')],
        [sg.VPush()],
        [sg.Button('Cancel'), sg.Button('Save'), sg.Push()]]
    
    scrollable_settings_layout = [[sg.Text("Test")],[sg.Column(settings_layout)]]
    
    # Create the Window
    window = sg.Window('Settings', scrollable_settings_layout, size=(config["gui_sett_x"], config["gui_sett_y"]), icon='AJ.ico')
    
    while True:
        event, values = window.read()
        
        if event == 'Cancel':
            window.close()
            open_input_window()
            break
        
        if event == 'ThemeListBox':
            selected_theme = values['ThemeListBox'][0]
            sg.theme(selected_theme)  # Apply the selected theme
            
        if event == 'Save':
            selected_theme = values['ThemeListBox'][0]
            config["theme"] = selected_theme  # Save the selected theme
            sg.theme(selected_theme)  # Apply the selected theme
            Config.write()
            window.close()
            open_input_window()
            break
        
        # if user closes window
        if event == sg.WIN_CLOSED:
            Config.write()
            break

#██╗███╗   ██╗██████╗ ██╗   ██╗████████╗    ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗
#██║████╗  ██║██╔══██╗██║   ██║╚══██╔══╝    ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║
#██║██╔██╗ ██║██████╔╝██║   ██║   ██║       ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║
#██║██║╚██╗██║██╔═══╝ ██║   ██║   ██║       ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║
#██║██║ ╚████║██║     ╚██████╔╝   ██║       ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝
#╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝    ╚═╝        ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ 

def open_input_window():
    # Update the config to the latest values
    Config.read()
    
    input_layout = [
        [sg.Text("Press 'Generate Report' to automatically enter all the Shiftnote and S&L information"), sg.Push(), sg.Button('⚙ Settings', size=(10, 1),  enable_events=True, font=('Arial', 12), key="settings")],
        [sg.Checkbox("Save Reports", key='save'),sg.Push(),sg.Button('Payroll Tool', key="-PAY-")],
        [
            sg.Button("Start Auto Close", size=(15, 2), font=("Georgia", 12, 'bold')), sg.Push(), 
            sg.Button(button_text="Saved Reports", size=(12, 2), key="-LOAD-", font=("Georgia", 12))
        ],
        [sg.Output(size=(config["gui_out_x"], config["gui_out_y"]), key="-OUTPUT-")]
]   
    
    # Create the window
    window = sg.Window("AutoJustin V2", input_layout, finalize=True, icon='AJ.ico')
    curr_shift = None

    # Update the gui elements with the old values from the config
    window["save"].update(config["save_reports"])          

    try:
    # Event loop
        while True:
            event, values = window.read()
            
            if event == "-LOAD-":
                DL.logger.info("\n\n   - Loading Report -")
                # Find the .shift file and load it in as a Shift class
                load_path = sg.popup_get_file('Pick a saved shift to load', initial_folder=config["saved_reports_dir"], file_types=[("Shift Files","*.shift")])
                loaded_shift = load_shift_file(load_path)
                
                # Start timer after human input
                sg.timer_start()
                
                # print loaded shift
                # This allows for older shift files to still be backwards compatible
                updated_shift = Shift(DCDictionary(loaded_shift.encaped_data.Ndfs_arr))
                updated_shift.print_member_variables()
                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                print(updated_shift.get_hourly_report_str())
                print(updated_shift.get_sales_proj_vs_act_perc())
                print(updated_shift.get_sales_proj_vs_act_labor())
                print(updated_shift.get_present_job_title_count())
                
                DL.logger.debug(f"[LOAD Time]: {(sg.timer_stop()):0.2f}ms")
                sg.timer_start()
                
            if event == "settings":
                window.close()
                open_settings_window()
                break
                
            if event == "Start Auto Close":
                sg.timer_start()
                
                # Update all the settings and file paths from the gui elements to the config
                DL.logger.info("\n   - Generating Report -")
                config["save_reports"] = values["save"]
                Config.write()
                
                # Log Config Read Write Time
                DL.logger.debug(f"[Config RW Time]: {sg.timer_stop()}ms")
                sg.timer_start()
                
                DL.logger.info("Downloading the latest S&L file...")
                SugarSync.connect()
                sl_filename = SugarSync.download_dated_SL_file(date.today(), config["temp_dir"])
                DL.logger.info(f"Downloaded: {sl_filename}")
                
                DL.logger.debug(f"[S&L Download Time]: {sg.timer_stop()}ms")
                sg.timer_start()
                
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
                
                DL.logger.debug(f"[Download CSV Time]: {sg.timer_stop()}ms")
                sg.timer_start()
            
                # Convert all the needed csv files in temp to a DCArray
                # Then create a Shift object with it
                try:
                    encapsulated_data = DRW.create_ecapsulated_data(config["temp_dir"], config["temp_dir"])
                    
                    DL.logger.debug(f"[Data Encapsulation Time]: {sg.timer_stop}ms")
                    sg.timer_start()
                    
                    curr_shift: Shift = Shift(encapsulated_data)
                    
                    DL.logger.debug(f"[Encaped Data Read Time]: {sg.timer_stop()}ms")
                    sg.timer_start()
            
                    if config['save_reports']:
                        save_shift_file(curr_shift)
                        
                    DL.logger.debug(f"[Report Save Time]: {sg.timer_stop()}ms")
                    sg.timer_start()
                    
                    # Write data into the temp S&L then upload tmep S&L to SugarSync
                    DRW.write_shift_into_sl(curr_shift)
                    SugarSync.upload_sl_file(date.today(), DRW.find_full_sl_path(config["temp_dir"]))
                    
                    DL.logger.debug(f"[SugarSync Upload Time]: {sg.timer_stop()}ms")
                    sg.timer_start()
                    
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
                    
                DL.logger.debug(f"[Enter ShiftNote Time]: {sg.timer_stop()}ms")
                sg.timer_start()
                    
                # Print all the data because its cool
                try:
                    curr_shift.print_member_variables()
                    print(curr_shift.get_hourly_report_str())
                    print(curr_shift.get_sales_proj_vs_act_perc())
                    print(curr_shift.get_sales_proj_vs_act_labor())
                    print(curr_shift.get_present_job_title_count())
                    
                except Exception as e:
                    DL.logger.error("ERROR: Failed to print shift details! Exception:")
                    DL.logger.exception(e)
                    
                DL.logger.debug(f"[Print and Save Time]: {sg.timer_stop()}ms")

            # Update all the settings and file paths from the gui elements to the config
            # When the window closes
            if event == sg.WIN_CLOSED:
                Config.write()
                break
                
    # Just catch any possible exception that way the gui doesn't just suddenly close
    except Exception as e:
        DL.logger.exception(e)
        DL.logger.critical("A Critical Error Occured!")
        DL.logger.critical("-= Restarting window in 5 seconds! =-")
        time.sleep(5)
        open_start_window()

    # Close the window just in case it gets stuck somehow
    window.close()
    
if __name__ == "__main__":
    open_start_window()
