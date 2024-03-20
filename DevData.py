from math import nan
import os
import numpy as np
from pandas import DataFrame as df

class NamedDataFrame:
    def __init__(self, file_path: str, dataframe: df):
        self.folder_path, self.file_name = os.path.split(file_path)
        self.dataframe = dataframe

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
        self.df.iat[self.row_index, self.col_index] = value
        
        # Save the modified DataFrame back to the file
        if(self.file_ext == ".csv"):
            self.df.to_csv(self.full_file_path, index=False)
            
        # Writitng to an excel file this way strips all its formatting 
        # TODO use openpyxl to preserve the formating of excel file
        #elif(self.file_ext == ".xlsx"):
        #    self.df.to_excel(self.full_file_path, index=False)
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
        
        for Ndf in self.Ndfs_arr:
            for i in range(len(Ndf.dataframe.index)):
                for j in range(len(Ndf.dataframe.columns)):
                    cellval = Ndf.dataframe.iat[i, j]
                    if (cellval != 0) and (str(cellval) != "nan"):
                        self.DCArr.append(DataCell(Ndf, i, j))
                        
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
        return [cell for cell in self.DCArr if cell.signature == sig]
    
    def read_by_sign(self, sig: str):
        '''
            This returns an array of values for every value within a given signature
            
            If a Datacell for that signature doesn't exist function returns 0
        '''
        values = [val.read() for val in self.get_dc_by_sign(sig)]
        
        numVals = len(values)
        
        if numVals == 0: 
            # This print seemed like a good idea, but it got old fast lol
            #print(f"WARNING: No DC found for cell signature: [{sig}]")
            values = 0
        elif numVals == 1:
            values = values[0]
        
        return values
    
    def read_by_sign_sum_results(self, sig: str):
        '''
            This returns the sum of all the Datacell's values
        '''
        
        data = self.read_by_sign(sig)

        return sum(data) if type(data) is list else data




        
    
    