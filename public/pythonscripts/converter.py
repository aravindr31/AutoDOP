import win32com.client as win32
import os
import sys

fileName = sys.argv[1]
fPath = "C:\\Users\\aravi\\Documents\\RD\\xlsFile\\"+fileName
outpath = "C:\\Users\\aravi\\Documents\\RD\\xlsxFile"
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(fPath)
wb.SaveAs(outpath + "/"+fileName , FileFormat=51)
wb.Close()
excel.Quit()
print("Conversion Completed")

