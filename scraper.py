from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
stringNumber = sys.argv[3]
accNumbers = list(map(str, stringNumber.split(',')))
rebateString = sys.argv[4]
rebate = list(map(int, rebateString.split(',')))


driver.get("https://dopagent.indiapost.gov.in/")

def loginPage():
    # Fixed deprecated find_element_by_id
    login = driver.find_element(By.ID, "AuthenticationFG.USER_PRINCIPAL")
    login.clear()
    login.send_keys(sys.argv[1])
    login = driver.find_element(By.ID, "AuthenticationFG.ACCESS_CODE")
    login.clear()
    login.send_keys(sys.argv[2])


def accountsPage():
    try:
        accounts = WebDriverWait(driver, 360).until(
            EC.presence_of_element_located((By.ID, "Accounts"))
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

    # Fixed deprecated find_element_by_id
    fetchAccounts = driver.find_element(By.ID, "CustomAgentRDAccountFG.ACCOUNT_NUMBER_FOR_SEARCH")
    noOfAccounts = len(accNumbers)
    for i in accNumbers:
        fetchAccounts.send_keys(i, ",")
    AccountNumbers = []
    # Fixed deprecated find_element_by_id
    fetch = driver.find_element(By.ID, "Button3087042")
    fetch.click()
    x = 0
    while x < noOfAccounts:
        if x == 10:
            # Fixed deprecated find_element_by_id
            nextPage = driver.find_element(By.ID, "Action.AgentRDActSummaryAllListing.GOTO_NEXT__")
            nextPage.click()

        y = str(x)
        # Fixed deprecated find_element_by_id
        selectAccount = driver.find_element(By.ID, "CustomAgentRDAccountFG.SELECT_INDEX_ARRAY[" + y + "]")
        selectAccount.click()
        x += 1
    # Fixed deprecated find_element_by_id
    saveAccounts = driver.find_element(By.ID, "Button26553257")
    saveAccounts.click()
    try:
        pay = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
        )
    except:
        driver.quit()

def paymentPage():
    p = 0
    for m, n in zip(accNumbers, rebate):
        q = str(p)
        if n != 1:
            if p >= 10:
                # Fixed deprecated find_element_by_id
                rebateNextPage = driver.find_element(By.ID, "Action.SelectedAgentRDActSummaryListing.GOTO_NEXT__")
                rebateNextPage.click()

            # Fixed deprecated find_element_by_xpath
            rebateNextAcc = driver.find_element(By.XPATH, "//input[@value='" + q + "']")
            rebateNextAcc.click()
            # Fixed deprecated find_element_by_id
            rebateValue = driver.find_element(By.ID, "CustomAgentRDAccountFG.RD_INSTALLMENT_NO")
            rebateValue.clear()
            rebateValue.send_keys(n)
            # Fixed deprecated find_element_by_id
            saveRebate = driver.find_element(By.ID, "Button11874602")
            saveRebate.click()
            time.sleep(3)
            
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

    # Fixed deprecated find_element_by_id with Select
    status = Select(driver.find_element(By.ID, "CustomAgentRDAccountFG.INSTALLMENT_STATUS"))
    status.select_by_value("SUC")

    # Fixed deprecated find_element_by_id
    search = driver.find_element(By.ID, "SearchBtn")
    search.click()

    time.sleep(4)

    # Fixed deprecated find_element_by_id with Select
    status = Select(driver.find_element(By.ID, "CustomAgentRDAccountFG.OUTFORMAT"))
    status.select_by_value("4")

    # Fixed deprecated find_element_by_id
    search = driver.find_element(By.ID, "SearchBtn")

    # Fixed deprecated find_element_by_id
    ok = driver.find_element(By.ID, "GENERATE_REPORT")
    ok.click()

def main():  
    loginPage()
    time.sleep(1)
    accountsPage()
    paymentPage()
    time.sleep(5)
    driver.quit()

main()