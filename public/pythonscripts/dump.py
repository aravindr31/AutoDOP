import glob
import os
import sys

count = sys.argv[1]
folder = "C:\\Users\\Aravind\\Documents\\RD\\xlsFile\\*"
list_of_files = glob.glob(folder) # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
lFName = os.path.basename(latest_file)
Newname = count+" "+lFName

os.rename("C:\\Users\\Aravind\\Documents\\RD\\xlsFile\\"+lFName,"C:\\Users\\Aravind\\Documents\\RD\\xlsFile\\"+Newname)