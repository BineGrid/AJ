from math import nan
import os
import numpy as np
from pandas import DataFrame as df
from openpyxl import workbook
import time
import DevLogger as DL

class NamedDataFrame:
    '''
        Added a name var and a sheet_name to the pandas dataframe\n
        Files with a xl_sheet are just excel files
    '''
    def __init__(self, file_path: str, dataframe: df, xl_sheet: workbook = None, xl_workbook: workbook = None):
        self.folder_path, self.file_name = os.path.split(file_path)
        self.dataframe = dataframe
        self.xl_sheet = xl_sheet
        self.xl_workbook = xl_workbook

class DataCell:
    '''
        - This class is essentially just a single cell within a df

        - This cell can be read or written to and contains the actually df
        that the cell is within so it will update dynamically 
        
        - These Data cells are refered to by their signature.
        A signature is just a string that is defined as "filename-row-col"
        
        - A row is just the val of the nearest string to the left of the DataCell
        
        - A col is just the val of the nearest string above the DataCell
        
        - DataCells can also just have a file name and col value and no row
        The signature would just be "filename-col"
        Just set row_name = None to have no row
    '''
    
    def __init__(self, Ndf: NamedDataFrame, row_index: int, col_index: int):
        self.file_path = Ndf.folder_path
        self.df = Ndf.dataframe
        self.xl_sheet = Ndf.xl_sheet
        self.xl_workbook = Ndf.xl_workbook
        self.row_index = row_index
        self.col_index = col_index
        self.full_file_path = os.path.join(Ndf.folder_path, Ndf.file_name)
        
        # This removes the ext from the filename
        self.file_name, self.file_ext = os.path.splitext(Ndf.file_name)
        
        # If its an S&L or Payroll file just shorten the name for convenience
        if self.file_name.startswith("S&L"):
            self.file_name = "S&L"
        elif self.file_name.startswith("PayrollExport"):
            self.file_name = "Payroll"
            
        self.row_name = self.__find_row_name()
        self.col_name = self.__find_col_name()
    
        if self.row_name is None:
            self.signature = f"{self.file_name}-{self.col_name}"
        else:
            self.signature = f"{self.file_name}-{self.row_name}-{self.col_name}"
            
    def __is_name_valid(self, name: str):
        strings_to_remove = [".", " "]
        for string in strings_to_remove:
            name = name.replace(string, "")
            
        return not name.isdigit() and name != "nan"
            
    def __find_col_name(self):
        '''
            Finds the nearest string above the given cell
            This string is considered the col_name
            
            If no col_name is found the name will default to the
            list of col_name's within the df with the same c_index
        '''
        # Slice the df & Grab the column I want as a numpy array
        cols = self.df.iloc[ :(self.row_index), self.col_index].values
        
        # If we are on row 0 then the col name is just the column header name
        if(self.row_index == 0):
            return self.df.columns[self.col_index]
        
        result = self.df.columns[self.col_index]
        
        # Cycle thru cols if one isn't a number and isnlt "nan" then thats the new col_name
        # The last string should be the closest string to the cell
        for val in cols:
            if self.__is_name_valid(str(val)):
                result = val
            
        return result
    
    def __find_row_name(self):
        '''
            Finds the nearest string to the left of the given cell
            This string is considered the row_name
            
            Returns None if no string is found
        '''
        result = None
        
        rows = self.df.iloc[self.row_index, 0:self.col_index].values
        
        for val in rows:
            if self.__is_name_valid(str(val)):
                result = val
            
        return result
            
    def read(self):
        return self.df.iat[self.row_index, self.col_index]
    
    def write(self, value):
        '''
            This writes to a single DataCell and updates the actual file
        '''
        
        # Save the modified DataFrame back to the file
        if(self.file_ext == ".csv"):
            self.df.iat[self.row_index, self.col_index] = value
            self.df.to_csv(self.full_file_path, index=False)
            
        elif(self.file_ext == ".xlsx"):
            # +2 and +1 are for the proper shift between openpyxl between pandas df
            self.xl_sheet.cell(self.row_index + 2, self.col_index + 1).value = value
            self.xl_workbook.save(self.full_file_path)
        else:
            raise ValueError(f"Unsupported file type for DataCell.write(): {self.file_ext}")
    
    def print(self):
        '''
            Prints every signature from the class
            and the cell value
        '''
        print(f"signature: {self.signature}")
        print(f"val: {self.read()}")
            

        
class DCArray:
    '''
        This stands for DataCellArray
        
        This takes in a df array and creates DataCell array 
        and then offers helpful functions to make using a 
        DataCell array easier and more friendly :)
    '''
        
    def __init__(self, Ndfs_arr: list):
        self.DCArr = []
        self.Ndfs_arr = Ndfs_arr
        self.signature_dict = {}  # Dictionary to store lists of DataCells by signature

        cum_dc_time = 0
        start_time = time.process_time()
        for Ndf in self.Ndfs_arr:
            for i in range(len(Ndf.dataframe.index)):
                for j in range(len(Ndf.dataframe.columns)):
                    dc_start_time = time.process_time_ns()
                    data_cell = DataCell(Ndf, i, j)
                    dc_end_time = time.process_time_ns()
                    cum_dc_time += (dc_end_time - dc_start_time)
                    self.DCArr.append(data_cell)

                    # Add the DataCell to the dictionary indexed by its signature
                    if data_cell.signature not in self.signature_dict:
                        self.signature_dict[data_cell.signature] = [data_cell]
                    else:
                        self.signature_dict[data_cell.signature].append(data_cell)
        
        end_time = time.process_time()
        DL.logger.debug(f"[DC Dictionary Creation Time]: {(end_time - start_time):0.4f}s")
        DL.logger.debug(f"[Avg Individual DC]: {((cum_dc_time / 100) / len(self.signature_dict)):0.4f}ms")
                        
    def size(self):
        return len(self.DCArr)
                    
    def print(self):
        for dc in self.DCArr:
            dc.print()
            print("=================================")
        print(f"Total DataCells: {len(self.DCArr)}")
                    
    def get_dc_by_sign(self, sig: str):
        '''
            This returns an array of all the cells with the same signature
        '''
        return self.signature_dict.get(sig, [])
    
    def read_by_sign(self, sig: str):
        '''
            This returns an array of values for every value within a given signature
            
            If a Datacell for that signature doesn't exist function returns 0
        '''
        values = [val.read() for val in self.get_dc_by_sign(sig)]
        
        numVals = len(values)
        
        # If we dont find a value just return 0
        if numVals == 0: 
            values = 0
        # If its just a single value, remove the list property
        elif numVals == 1:
            values = values[0]
        
        return values
    
    def write_by_sign(self, sig: str, val):
            for dc in self.get_dc_by_sign(sig):
                dc.write(val)
    
    def read_by_sign_sum_results(self, sig: str):
        '''
            This returns the sum of all the Datacell's values
        '''
        
        data = self.read_by_sign(sig)

        return sum(data) if type(data) is list else data




        
    
    