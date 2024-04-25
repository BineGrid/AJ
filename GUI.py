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
    DL.logger.critical("PySimpleGUI doesn't seem to be installed properly.")
    DL.logger.critical("Exception: ", e)

config = Config.get_config()

#███████╗████████╗ █████╗ ██████╗ ████████╗    ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗
#██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝    ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║
#███████╗   ██║   ███████║██████╔╝   ██║       ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║
#╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║
#███████║   ██║   ██║  ██║██║  ██║   ██║       ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝
#╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ 

def open_start_window():
    sg.theme(config["theme"])
    
    start_layout = [
        [
            sg.Button('Payroll Buddy', key="-PAY-"), sg.Push(), sg.Text("Welcome to ", font=("Georgia", 20, 'bold')),
            sg.Text("AJ", font=("Impact", 28), text_color="gold"), sg.Push(), sg.Button("Config.json")
        ],
        [sg.Push(), sg.Text("Please select a tool", font=("Georgia", 14, 'bold')), sg.Push()],
        [sg.Button("Auto Closer", size=(12, 2)), sg.Push(), sg.Button("⚙ Settings", key="settings", size=(12, 2))]]
    
    window = sg.Window('Starting Window', start_layout, size=(config["gui_start_x"], config["gui_start_y"]), icon='AJ.ico')

    while True:
        event, values = window.read()
        
        if event == "-PAY-":
            window.close()
            open_paytool_window()
            break
        
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
            Config.write(config)
            break
    
#███████╗███████╗████████╗████████╗██╗███╗   ██╗ ██████╗ ███████╗
#██╔════╝██╔════╝╚══██╔══╝╚══██╔══╝██║████╗  ██║██╔════╝ ██╔════╝
#███████╗█████╗     ██║      ██║   ██║██╔██╗ ██║██║  ███╗███████╗
#╚════██║██╔══╝     ██║      ██║   ██║██║╚██╗██║██║   ██║╚════██║
#███████║███████╗   ██║      ██║   ██║██║ ╚████║╚██████╔╝███████║
#╚══════╝╚══════╝   ╚═╝      ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
    
# This is to remember the theme you selected when the window refreshes
last_selected_theme = None    
    
def open_settings_window():
    
    settings_layout = [
        [sg.Push(), sg.Text("Settings", font=("Arial", 20, 'bold')), sg.Push()],
        [sg.Push(), sg.Text('Change the Color Scheme', font=('Arial', 12, 'bold')), sg.Push()],
        [
         sg.Push(),
         sg.Listbox(sg.theme_list(), enable_events=True, size=(21, 10), k='-Theme-'),
         sg.Push(),
        ],
        [sg.Push(), sg.Input(s=(22, 1), default_text=config["theme"], k="-ThemeIn-",), sg.Push()],
        [sg.Text("")],
        [sg.Push(), sg.Text('Window Sizes', font=('Arial', 12, 'bold')), sg.Push()],
        [
         sg.Push(),
         sg.Text("Start-X:"), sg.Input(s=(4, 1), k="-StX-", default_text=config["gui_start_x"]), 
         sg.Text("Output-X:"), sg.Input(s=(4, 1), k="-OutX-", default_text=config["gui_out_x"]), 
         sg.Text("Settings-X:"), sg.Input(s=(4, 1), k="-SetX-", default_text=config["gui_sett_x"]),
         sg.Text("Paytool-X:"), sg.Input(s=(4, 1), k="-PayX-", default_text=config["gui_paytool_x"]),
         sg.Push()
        ],
        [
         sg.Push(),
         sg.Text("Start-Y:"), sg.Input(s=(4, 1), k="-StY-", default_text=config["gui_start_y"]), 
         sg.Text("Output-Y:"), sg.Input(s=(4, 1), k="-OutY-", default_text=config["gui_out_y"]), 
         sg.Text("Settings-Y:"), sg.Input(s=(4, 1), k="-SetY-", default_text=config["gui_sett_y"]),
         sg.Text("Paytool-Y:"), sg.Input(s=(4, 1), k="-PayY-", default_text=config["gui_paytool_y"]),
         sg.Push()
        ],
        [sg.Text("")],
        [sg.Push(), sg.Text('Misc', font=('Arial', 12, 'bold')), sg.Push()],
        [
         sg.Push(),
         sg.Text("Image Confidence:"), sg.Input(s=(4, 1), k="-ImConf-", default_text=config["image_click_confidence"]), 
         sg.Text("Web Loading Wait:"), sg.Input(s=(4, 1), k="-LoadWait-", default_text=config["DEFAULT_LOADING_WAIT"]), 
         sg.Text("Web Download Wait"), sg.Input(s=(4, 1), k="-DownWait-", default_text=config["DEFAULT_DOWNLOAD_WAIT"]),
         sg.Push()
        ],
        [sg.VPush()],
        [sg.Button('Save'), sg.Button('Cancel'), sg.Push(), sg.Button('Open Config')]
    ]
    
    # Create the Window
    window = sg.Window('Settings', settings_layout, size=(config["gui_sett_x"], config["gui_sett_y"]), icon='AJ.ico')
    
    global last_selected_theme
    
    while True:
        event, values = window.read()
        
        if event == 'Cancel':
            sg.theme(config["theme"])
            window.close()
            open_input_window()
            break
        
        if event == "Open Config":
            os.startfile("config.json")
        
        if event == '-Theme-':
            selected_theme = values['-Theme-'][0]
            sg.theme(selected_theme)  
            window.close()
            last_selected_theme = selected_theme
            open_settings_window()
            
        if event == 'Save':
            if values["-ThemeIn-"] == config["theme"]:
                config["theme"] = last_selected_theme
            else:
                config["theme"] = values["-ThemeIn-"]
                last_selected_theme = values["-ThemeIn-"]
                
            config["gui_start_x"] = values["-StX-"]
            config["gui_start_y"] = values["-StY-"]
            config["gui_out_x"] = values["-OutX-"]
            config["gui_out_y"] = values["-OutY-"]
            config["gui_sett_x"] = values["-SetX-"]
            config["gui_sett_y"] = values["-SetY-"]
            config["gui_paytool_x"] = values["-PayX-"]
            config["gui_paytool_y"] = values["-PayY-"]
            config["image_click_confidence"] = values["-ImConf-"]
            config["DEFAULT_LOADING_WAIT"] = values["-LoadWait-"]
            config["DEFAULT_DOWNLOAD_WAIT"] = values["-DownWait-"]
            
            sg.theme(last_selected_theme)  
            Config.write(config)
            window.close()
            open_input_window()
            break
        
        # if user closes window
        if event == sg.WIN_CLOSED:
            Config.write(config)
            break

#██╗███╗   ██╗██████╗ ██╗   ██╗████████╗    ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗
#██║████╗  ██║██╔══██╗██║   ██║╚══██╔══╝    ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║
#██║██╔██╗ ██║██████╔╝██║   ██║   ██║       ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║
#██║██║╚██╗██║██╔═══╝ ██║   ██║   ██║       ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║
#██║██║ ╚████║██║     ╚██████╔╝   ██║       ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝
#╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝    ╚═╝        ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ 

def open_input_window():
    
    ans: str = ""
    
    input_layout = [
        [sg.Text("Press 'Start Auto Close' to automatically enter all the Shiftnote and S&L information"), sg.Push(), sg.Button('⚙ Settings', size=(10, 1),  enable_events=True, font=('Arial', 12), key="settings")],
        [sg.Checkbox("Save Reports", key='save'),sg.Push(),sg.Button('Payroll Tool', key="-PAY-")],
        [
            sg.Button("Start Auto Close", size=(15, 2), font=("Arial", 12, 'bold')), sg.Push(), 
            sg.Button(button_text="Saved Reports", size=(12, 2), key="-LOAD-", font=("Arial", 12))
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
                print(updated_shift.create_hourly_report_str())
                print(updated_shift.create_sales_proj_vs_act_perc())
                print(updated_shift.create_sales_proj_vs_act_labor())
                print(updated_shift.create_present_job_title_count())
                
                DL.logger.debug(f"[LOAD Time]: {(sg.timer_stop()):0.2f}ms")
                sg.timer_start()
                
            if event == "settings":
                window.close()
                open_settings_window()
                break
            
            if event == "-PAY-":
                window.close()
                open_paytool_window()
                break
                
            if event == "Start Auto Close":
                
                # Delete all files in temp if config says so
                if config["delete_temp_files"]:
                    DRW.delete_everything_in_dir(config["temp_dir"])
                
                sg.timer_start()
                
                # Update all the settings and file paths from the gui elements to the config
                DL.logger.info("\n   - Generating Report -")
                config["save_reports"] = values["save"]
                Config.write(config)
                
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
                    
                    # Prompt the user to check if the info is correct before inputting it
                    info = curr_shift.hourly_report_str + "\n" + curr_shift.sales_proj_vs_act_labor + "\n" + curr_shift.sales_proj_vs_act_perc + "\n" + curr_shift.present_job_title_count
                    ans: str = sg.popup_get_text("Is this information correct?\n", title="Double Check", default_text=info, size=(60, 25))
                    
                    sg.timer_start()
                    
                    if not(ans.lower() == "cancel"):
                        inputed_shift_strs = ans.split("\n\n")
                        
                        curr_shift.hourly_report_str = inputed_shift_strs[0]
                        curr_shift.sales_proj_vs_act_labor = inputed_shift_strs[1]
                        curr_shift.sales_proj_vs_act_perc = inputed_shift_strs[2]
                        curr_shift.present_job_title_count = inputed_shift_strs[3] 
                        
                        # Write data into the temp S&L then upload tepp S&L to SugarSync
                        DRW.write_shift_into_sl(curr_shift)
                        SugarSync.upload_sl_file(date.today(), DRW.find_full_sl_path(config["temp_dir"]))
                        
                        DL.logger.debug(f"[SugarSync Upload Time]: {sg.timer_stop()}ms")
                        sg.timer_start()
                        
                        try:
                            Web.ShiftNote.enter_shift(Web.ShiftNote, curr_shift)
                        except Exception as e:
                            DL.logger.error("ERROR:nan Failed to input shift into ShiftNote")
                            DL.logger.exception(e)
                        
                    DL.logger.debug(f"[Enter ShiftNote Time]: {sg.timer_stop()}ms")
                    sg.timer_start()
                    
                    # Delete all files in temp if config says so
                    if config["delete_temp_files"]:
                        DRW.delete_everything_in_dir(config["temp_dir"])
                        
                except Exception as e:
                    DL.logger.error("ERROR: Failed to read CSV files")
                    DL.logger.exception(e)

                    
                # Print all the data because its cool
                try:
                    curr_shift.print_member_variables()
                    
                except Exception as e:
                    DL.logger.error("ERROR: Failed to print shift details! Exception:")
                    DL.logger.exception(e)
                    
                DL.logger.debug(f"[Print and Save Time]: {sg.timer_stop()}ms")

            # Update all the settings and file paths from the gui elements to the config
            # When the window closes
            if event == sg.WIN_CLOSED:
                Config.write(config)
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
    
    
#██████╗  █████╗ ██╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗     
#██╔══██╗██╔══██╗╚██╗ ██╔╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
#██████╔╝███████║ ╚████╔╝        ██║   ██║   ██║██║   ██║██║     
#██╔═══╝ ██╔══██║  ╚██╔╝         ██║   ██║   ██║██║   ██║██║     
#██║     ██║  ██║   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗
#╚═╝     ╚═╝  ╚═╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    
def open_paytool_window():
    sg.theme(config["theme"])
    
    start_layout = [[sg.Button("Cancel")]]
    
    window = sg.Window('Payroll Buddy :D', start_layout, size=(config["gui_paytool_x"], config["gui_paytool_y"]), icon='AJ.ico')
    
    while True:
        event, values = window.read()
        
        if event == "Cancel":
            window.close()
            open_input_window()
            break
        
        if event == sg.WIN_CLOSED:
            break
    
if __name__ == "__main__":
    open_start_window()
