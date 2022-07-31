import win32com.client as win32
import os
import sys

fileName = sys.argv[1]
fPath = "C:\\Users\\Aravind\\Documents\\RD\\xlsFile\\"+fileName
# fPath = "C:\\Users\\Aravind\\Documents\\RD\\xlsFile\\RDInstallmentReport31-07-2022"

outpath = "C:\\Users\\Aravind\\Documents\\RD\\xlsxFile"
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(fPath)
wb.SaveAs(outpath + "/"+fileName , FileFormat=51)
# wb.SaveAs(outpath + "/cid", FileFormat=51)

wb.Close()
excel.Quit()
print("Conversion Completed")

