from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import sys
import time


PATH = "C:\Program Files (x86)\chromedriver.exe" 
driver = webdriver.Chrome(PATH)
stringNumber = sys.argv[3]
accNumbers = list(map(str, stringNumber.split(',')))
rebateString = sys.argv[4]
rebate = list(map(int, rebateString.split(',')))


driver.get("https://dopagent.indiapost.gov.in/")
# print(driver.title)
def loginPage ():
    login = driver.find_element_by_id("AuthenticationFG.USER_PRINCIPAL")
    login.clear()
    login.send_keys(sys.argv[1])
    login = driver.find_element_by_id("AuthenticationFG.ACCESS_CODE")
    login.clear()
    login.send_keys(sys.argv[2])


def accountsPage():
    try:
        accounts = WebDriverWait(driver, 360).until(
            EC.presence_of_element_located((By.ID,"Accounts"))
        )
    except:
        driver.quit()

    accounts.click()
    try:
        mainPage = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Agent Enquire & Update Screen"))
        )
    except:
        driver.quit()

    mainPage.click()

    try:
        cash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "absmiddle"))
        )
    except:
        driver.quit()

    cash.click()

    fetchAccounts = driver.find_element_by_id(
        "CustomAgentRDAccountFG.ACCOUNT_NUMBER_FOR_SEARCH")
    # print(sys[1])
    # stringNumber = sys.argv[3]
    # accNumbers = list(map(str, stringNumber.split(',')))
    # print(accNumbers)
    noOfAccounts = len(accNumbers)
    # print(noOfAccounts)
    for i in accNumbers:
        fetchAccounts.send_keys(i, ",")
    AccountNumbers = []
    fetch = driver.find_element_by_id("Button3087042")
    fetch.click()
    x = 0
    while x < noOfAccounts:
        if x == 10:
            nextPage = driver.find_element_by_id(
                "Action.AgentRDActSummaryAllListing.GOTO_NEXT__")
            nextPage.click()

        y = str(x)
        selectAccount = driver.find_element_by_id(
            "CustomAgentRDAccountFG.SELECT_INDEX_ARRAY[" + y + "]")
        selectAccount.click()
        x += 1
    saveAccounts = driver.find_element_by_id("Button26553257")
    saveAccounts.click()
    try:
        pay = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
        )

    except:
        driver.quit()
# print("here")
# rebateString = sys.argv[4]
# rebate = list(map(int, rebateString.split(',')))

# print(len(rebate))
# print(rebate)
def paymentPage():
    p = 0
    for m, n in zip(accNumbers, rebate):
        q = str(p)
        if n != 1:

            if p >= 10:
                rebateNextPage = driver.find_element_by_id(
                    "Action.SelectedAgentRDActSummaryListing.GOTO_NEXT__")
                rebateNextPage.click()

            rebateNextAcc = driver.find_element_by_xpath(
                "//input[@value='" + q + "']")
            rebateNextAcc.click()
            rebateValue = driver.find_element_by_id(
                "CustomAgentRDAccountFG.RD_INSTALLMENT_NO")
            rebateValue.clear()
            rebateValue.send_keys(n)
            saveRebate = driver.find_element_by_id("Button11874602")
            saveRebate.click()
            time.sleep(3)
            # print("came upto here")
            try:
                pay = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
                )

            except:
                driver.quit()

        p += 1

        try:
            pay = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
            )

        except:
            driver.quit()

    pay.click()

    try:
        alertText = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MessageDisplay_TABLE']/div[2]"))
        )
        genNumber = alertText.text[53:63]
        print(genNumber)
    except:
        driver.quit()

    try:
        reports = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Reports"))
        )
    except:
        driver.quit()

    reports.click()

    try:
        cNumber = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "CustomAgentRDAccountFG.EBANKING_REF_NUMBER"))
        )
    except:
        driver.quit()

    cNumber.send_keys(genNumber)

    status = Select(driver.find_element_by_id(
        "CustomAgentRDAccountFG.INSTALLMENT_STATUS"))

    status.select_by_value("SUC")

    search = driver.find_element_by_id("SearchBtn")

    search.click()

    time.sleep(4)

    status = Select(driver.find_element_by_id("CustomAgentRDAccountFG.OUTFORMAT"))

    status.select_by_value("4")

    search = driver.find_element_by_id("SearchBtn")

    ok = driver.find_element_by_id("GENERATE_REPORT")

    ok.click()

# def check():
#     loginCheck= driver.find_element_by_xpath( "//*[@id='MessageDisplay_TABLE']/div[2]")
#     if loginCheck.text[11:20]=="characters":
#         loginPage()
#     return
        
loginPage()
time.sleep(1)
accountsPage()
paymentPage()

time.sleep(5)

driver.quit()
