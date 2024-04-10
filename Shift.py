from datetime import datetime
import json
import pickle
from DevData import *

with open('config.json') as f:
  config = json.load(f)

class Shift:
    '''
        This class is all the data for a single shift
    '''
    
    def __init__(self, encapsulated_data: DCArray):
        
        self.encaped_data = encapsulated_data
        
        # -= Misc =-
        self.currDay = encapsulated_data.read_by_sign("Day of week (totals)-Day of week")
        self.guestCount = encapsulated_data.read_by_sign(f"Day of week (totals)-{self.currDay}-Total guests")
        
        # -= Sales =-
        self.ProjSales = encapsulated_data.read_by_sign(f"S&L-NET Sales Projection-{self.currDay.upper()}")
        if isinstance(self.ProjSales, list):
            self.ProjSales = self.ProjSales[0] # We always get two of these, but I only want one lol
            
        self.netSales = encapsulated_data.read_by_sign(f"Day of week (totals)-{self.currDay}-Net sales")
        self.takeoutSales = encapsulated_data.read_by_sign("Revenue center summary-Take Out-Net sales")
        self.doordashSales = encapsulated_data.read_by_sign("Payments summary-Door Dash-Amount")
        self.grubhubSales = encapsulated_data.read_by_sign("Payments summary-Grubhub-Amount")
        self.foodSales = encapsulated_data.read_by_sign("Sales category summary-Food-Net sales")
        self.barSales = round(self.netSales - self.foodSales, 2)
        self.totalDiscounts = encapsulated_data.read_by_sign("Discount summary-Amount")
        
        # -= Labor =-
        self.ProjBOHHours = encapsulated_data.read_by_sign(f"S&L-Total Kitchen Hours-{self.currDay.upper()}")
        self.ProjFOHHours = encapsulated_data.read_by_sign(f"S&L-Total Front House Hours-{self.currDay.upper()}")
        self.ProjBOHLabor = encapsulated_data.read_by_sign(f"S&L-Total Kitchen Labor Cost-{self.currDay.upper()}")
        self.ProjFOHLabor = encapsulated_data.read_by_sign(f"S&L-Total Front Louse Cost-{self.currDay.upper()}")
        self.ProjBOHLaborPerc = round(encapsulated_data.read_by_sign(f"S&L-Total BOH Labor %-{self.currDay.upper()}"), 4)
        self.ProjFOHLaborPerc = round(encapsulated_data.read_by_sign(f"S&L-Total Front House %-{self.currDay.upper()}"), 4)
        
        # Grabs the names of all the respective Job titles from the config
        self.__FOHJobTitles = config.get("foh_job_titles", [])
        self.__BOHJobTitles = config.get("boh_job_titles", [])
        self.__MISCJobTitles = config.get("misc_job_titles", [])
        
        # init vars
        self.ActFOHHours = 0
        self.ActFOHLabor = 0
        self.ActBOHHours = 0
        self.ActBOHLabor = 0
        
        # This is an array of tuples that contains the job titles who are clocked in
        # And there amount of them i.e. [(3, "Cook"), (4, "Server")...]
        self.PresentJobCount_List = []
        
        # Cycle thru all the FOH jobs and add up there values
        for foh_job in self.__FOHJobTitles:
            self.ActFOHHours += encapsulated_data.read_by_sign_sum_results(f"Payroll-{foh_job}-Regular Hours")
            self.ActFOHHours += encapsulated_data.read_by_sign_sum_results(f"Payroll-{foh_job}-Overtime Hours")
            self.ActFOHLabor += encapsulated_data.read_by_sign_sum_results(f"Payroll-{foh_job}-Total Pay")

            # This counts how many people of a single job title are clocked in
            job_data = encapsulated_data.read_by_sign(f"Payroll-{foh_job}-Total Pay")
            if job_data == 0:
                pass
            elif type(job_data) is not list:
                self.PresentJobCount_List.append((1, f"{foh_job}"))
            else:
                self.PresentJobCount_List.append((len(job_data), f"{foh_job}"))
                
        
        # Cycle thru all the BOH jobs and add up there values
        for boh_job in self.__BOHJobTitles:
            self.ActBOHHours += encapsulated_data.read_by_sign_sum_results(f"Payroll-{boh_job}-Regular Hours")
            self.ActBOHHours += encapsulated_data.read_by_sign_sum_results(f"Payroll-{boh_job}-Overtime Hours")
            self.ActBOHLabor += encapsulated_data.read_by_sign_sum_results(f"Payroll-{boh_job}-Total Pay")
            
            # This counts how many people of a single job title are clocked in
            job_data = encapsulated_data.read_by_sign(f"Payroll-{boh_job}-Total Pay")
            if job_data == 0:
                pass
            elif type(job_data) is not list:
                self.PresentJobCount_List.append((1, f"{boh_job}"))
            else:
                self.PresentJobCount_List.append((len(job_data), f"{boh_job}"))
                
        # Cycle thru all the BOH jobs and add up there values
        for misc_job in self.__MISCJobTitles:
            
            # This counts how many people of a single job title are clocked in
            job_data = encapsulated_data.read_by_sign(f"Payroll-{misc_job}-Total Pay")
            if job_data == 0:
                pass
            elif type(job_data) is not list:
                self.PresentJobCount_List.append((1, f"{misc_job}"))
            else:
                self.PresentJobCount_List.append((len(job_data), f"{misc_job}"))

        self.ActFOHLaborPerc = round((self.ActFOHLabor / self.netSales), 4)
        self.ActBOHLaborPerc = round((self.ActBOHLabor / self.netSales), 4)

    def print_member_variables(self):
        '''
            Prints every member var and its contents from the entire class
        '''
        for var_name, var_value in vars(self).items():
            print(f"{var_name}: {var_value}")
                
    def get_hourly_report_str(self) -> str:
        '''
            The returns the Hour: Sales,Orders,Guest
            
            EX:
            4-5: $1200.00, 12 orders, 12 guests
            5-6: $1300.00, 13 orders, 13 guests
            ...
        '''
        result_string = "\n"
        
        # This puts every col into a list
        hours = (self.encaped_data.read_by_sign("Time of day (totals)-Hour of day"))
        sales_counts = (self.encaped_data.read_by_sign("Time of day (totals)-Net sales"))
        order_counts = (self.encaped_data.read_by_sign("Time of day (totals)-Total orders"))
        guest_counts = (self.encaped_data.read_by_sign("Time of day (totals)-Total guests"))
        
        # Cycle through all 4 list simultaneously, bc Python is awesome
        for hour, sales, orders, guests in zip(hours, sales_counts, order_counts, guest_counts):
            
            # Converts from military time to 12 hour
            hour = hour - 12 if hour > 12 else hour
            
            result_string += f"{hour}-{hour + 1}: ${sales}, {orders} orders, {guests} guests\n"
            
        return result_string
    
    def get_sales_proj_vs_act_perc(self) -> str:
        '''
            This:\n
            Sales Forecasted = $ Sales Actual = $ = $\n
            FOH Labor Forecasted % vs FOH Labor Actual %\n
            BOH Labor Forecasted % vs BOH Labor Actual %
        '''
        result_string = f"Sales Forecasted = ${self.ProjSales} Sales Actual = ${self.netSales} = "
        
        # Figure out the difference between proj and act sales
        sales_diff = round(self.netSales - self.ProjSales, 2)
        
        # Use the correct sign for the sales difference
        if sales_diff > 0:
            result_string += (f"+${sales_diff}\n")
        elif sales_diff == 0:
            result_string += (f"${sales_diff}\n")
        else:
            result_string += (f"-${abs(sales_diff)}\n")

        result_string += (f"FOH Labor Forecasted {round(self.ProjFOHLaborPerc * 100, 2)}% vs FOH Labor Actual {round(self.ActFOHLaborPerc * 100, 2)}%\n")
        result_string += (f"BOH Labor Forecasted {round(self.ProjBOHLaborPerc * 100, 2)}% vs BOH Labor Actual {round(self.ActBOHLaborPerc * 100, 2)}%\n")
        
        return result_string
    
    def get_sales_proj_vs_act_labor(self) -> str:
        '''
            This:\n
            FOH P: $ A: $\n
            BOH P: $ A: $
        '''
        result_string = f"FOH  P: ${round(self.ProjFOHLabor, 2)}  -  A: ${round(self.ActFOHLabor, 2)}\n"
        result_string += f"BOH  P: ${round(self.ProjBOHLabor, 2)}  -  A: ${round(self.ActBOHLabor, 2)}\n"
        
        return result_string
    
    def get_present_job_title_count(self) -> str:
        '''
            This:\n
                Bar 1/X Perfect\n
                Server 3/X Perfect\n
                Expo 1/X Perfect\n
                Cook 3/X Perfect\n
                Dish 1/X Perfect
        '''
        
        result_string = ""
        
        for count, job in self.PresentJobCount_List:
            result_string += f"{job} {count}/X Perfect\n"
        
        return result_string

def save_shift_file(shift: Shift):
    '''
        This will pickle a shift class and save it as a .shift file
        It gaves it a name based on the date and time
        
        Ex: M-D-Y_HourMinSec
    '''
    # Find current date and time to create the name of the file
    # datetime object containing current date and time
    now = datetime.now()

    # mm-dd-YY-H-M-S
    dt_string = now.strftime("%m-%d-%Y_%H%M%S")
    
    # Dump that shift as a .shift file based on the time and date
    with open(config["saved_reports_dir"] + f'/{dt_string}.shift', 'wb') as f:
        pickle.dump(shift, f)
    
def load_shift_file(file_path: str) -> Shift:
    '''
        This will unpickle a .shift file and return a shift object
    '''
    with open(file_path, 'rb') as f:
        return pickle.load(f)

            
            
