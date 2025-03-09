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
import json

def process_lists(list_data, username, password):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("https://dopagent.indiapost.gov.in/")
    results = []
    
    try:
        # Login once for all lists
        login_page(driver, username, password)
        time.sleep(1)
        
        # Process each list
        for list_item in list_data:
            list_name = list_item['name']
            account_numbers = list_item['numbers']
            rebate_values = list_item['rebate']
            
            print(f"Processing list: {list_name}")
            print(f"Account numbers: {account_numbers}")
            print(f"Rebate values: {rebate_values}")
            
            try:
                if driver.find_elements(By.ID, "AuthenticationFG.USER_PRINCIPAL")!=[]:
                    login_page(driver, username, password)
                    time.sleep(5)
                # Process this specific list
                accounts_page(driver, account_numbers, rebate_values)
                result = payment_page(driver, account_numbers, rebate_values)
                results.append({"list_name": list_name, "status": "success", "details": result})
                time.sleep(5)
                
            except Exception as e:
                print(f"Error processing list {list_name}: {str(e)}")
                results.append({"list_name": list_name, "status": "error", "details": str(e)})
    
    except Exception as e:
        print(f"Global error: {str(e)}")
        results.append({"status": "error", "details": f"Login or initialization failed: {str(e)}"})
    
    finally:
        driver.quit()
        return results

def login_page(driver, username, password):
    print("Inside Login Page")
    login = driver.find_element(By.ID, "AuthenticationFG.USER_PRINCIPAL")
    login.clear()
    login.send_keys(username)
    login = driver.find_element(By.ID, "AuthenticationFG.ACCESS_CODE")
    login.clear()
    login.send_keys(password)
    
    try:
        accounts = WebDriverWait(driver, 360).until(
            EC.presence_of_element_located((By.ID, "Accounts"))
        )
    except:
        driver.quit()

    accounts.click()

def accounts_page(driver, acc_numbers, rebate_values):
    print("inside Accounts page")
    try:
        mainPage = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Agent Enquire & Update Screen"))
        )
    except Exception as e:
        print(f"Failed to find 'Agent Enquire & Update Screen': {str(e)}")
        raise

    mainPage.click()

    try:
        cash = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "absmiddle"))
        )
    except Exception as e:
        print(f"Failed to find cash element: {str(e)}")
        raise

    cash.click()

    # Input account numbers
    fetchAccounts = driver.find_element(By.ID, "CustomAgentRDAccountFG.ACCOUNT_NUMBER_FOR_SEARCH")
    fetchAccounts.clear()
    no_of_accounts = len(acc_numbers)
    
    # Convert to comma-separated string if it's not already
    if isinstance(acc_numbers, list):
        account_numbers_str = ",".join(str(num).strip() for num in acc_numbers)
    else:
        account_numbers_str = acc_numbers
        
    fetchAccounts.send_keys(account_numbers_str)
    
    # Click fetch button
    fetch = driver.find_element(By.ID, "Button3087042")
    fetch.click()
    
    # Select all accounts
    x = 0
    while x < no_of_accounts:
        if x == 10:
            # Handle pagination
            try:
                nextPage = driver.find_element(By.ID, "Action.AgentRDActSummaryAllListing.GOTO_NEXT__")
                nextPage.click()
            except Exception as e:
                print(f"Pagination error: {str(e)}")
                # If no next page button, we might have fewer accounts than expected
                break

        try:
            y = str(x)
            selectAccount = driver.find_element(By.ID, f"CustomAgentRDAccountFG.SELECT_INDEX_ARRAY[{y}]")
            selectAccount.click()
            x += 1
        except Exception as e:
            print(f"Error selecting account at index {x}: {str(e)}")
            # If we can't find this account, move to next one
            x += 1
    
    # Save selected accounts
    saveAccounts = driver.find_element(By.ID, "Button26553257")
    saveAccounts.click()
    
    try:
        # Wait for pay element to be available
        pay = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
        )
    except Exception as e:
        print(f"Failed to find PAY_ALL_SAVED_INSTALLMENTS: {str(e)}")
        raise

def payment_page(driver, acc_numbers, rebate_values):
    # Convert to lists if they're not already
    if not isinstance(acc_numbers, list):
        acc_numbers = acc_numbers.split(',')
    
    if not isinstance(rebate_values, list):
        rebate_values = rebate_values.split(',')
    
    # Ensure rebate_values are integers
    rebate_values = [int(r) for r in rebate_values]
    
    p = 0
    for account_num, rebate_val in zip(acc_numbers, rebate_values):
        q = str(p)
        
        # Only process accounts with rebate values not equal to 1
        if rebate_val != 1:
            if p >= 10:
                try:
                    # Pagination for rebate
                    rebateNextPage = driver.find_element(By.ID, "Action.SelectedAgentRDActSummaryListing.GOTO_NEXT__")
                    rebateNextPage.click()
                except Exception as e:
                    print(f"Rebate pagination error: {str(e)}")
                    # Continue if no next page

            try:
                # Select account for rebate
                rebateNextAcc = driver.find_element(By.XPATH, f"//input[@value='{q}']")
                rebateNextAcc.click()
                
                # Set rebate value
                rebateValue = driver.find_element(By.ID, "CustomAgentRDAccountFG.RD_INSTALLMENT_NO")
                rebateValue.clear()
                rebateValue.send_keys(rebate_val)
                
                # Save rebate
                saveRebate = driver.find_element(By.ID, "Button11874602")
                saveRebate.click()
                time.sleep(3)
                
                # Wait for pay element again
                try:
                    pay = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
                    )
                except Exception as e:
                    print(f"Pay element not found after setting rebate: {str(e)}")
            except Exception as e:
                print(f"Error setting rebate for account {account_num}: {str(e)}")
                
        p += 1

    # Proceed with payment
    try:
        pay = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PAY_ALL_SAVED_INSTALLMENTS"))
        )
        pay.click()
    except Exception as e:
        print(f"Pay button not found: {str(e)}")
        raise

    # Get generated number
    gen_number = ""
    try:
        alertText = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='MessageDisplay_TABLE']/div[2]"))
        )
        gen_number = alertText.text[53:63]
        print(f"Generated number: {gen_number}")
    except Exception as e:
        print(f"Failed to get generated number: {str(e)}")
        raise

    # Navigate to reports
    try:
        reports = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Reports"))
        )
        reports.click()
    except Exception as e:
        print(f"Reports button not found: {str(e)}")
        raise

    # Enter generated number
    try:
        cNumber = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "CustomAgentRDAccountFG.EBANKING_REF_NUMBER"))
        )
        cNumber.send_keys(gen_number)
    except Exception as e:
        print(f"CNumber input not found: {str(e)}")
        raise

    # Set status
    try:
        status = Select(driver.find_element(By.ID, "CustomAgentRDAccountFG.INSTALLMENT_STATUS"))
        status.select_by_value("SUC")
    except Exception as e:
        print(f"Status select not found: {str(e)}")
        raise

    # Search
    try:
        search = driver.find_element(By.ID, "SearchBtn")
        search.click()
        time.sleep(4)
    except Exception as e:
        print(f"Search button not found: {str(e)}")
        raise

    # Set output format
    try:
        status = Select(driver.find_element(By.ID, "CustomAgentRDAccountFG.OUTFORMAT"))
        status.select_by_value("4")
    except Exception as e:
        print(f"Output format select not found: {str(e)}")
        raise

    # Generate report
    try:
        ok = driver.find_element(By.ID, "GENERATE_REPORT")
        ok.click()
        time.sleep(3)
    except Exception as e:
        print(f"Generate report button not found: {str(e)}")
        raise
    return {"gen_number": gen_number}

# Main execution when script is run
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scraper.py username password lists_json")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    # Parse the JSON data of lists
    lists_json = sys.argv[3]
    try:
        lists_data = json.loads(lists_json)
    except json.JSONDecodeError:
        print("Invalid JSON format for lists data")
        sys.exit(1)
    
    # Process all lists
    results = process_lists(lists_data, username, password)
    
    # Output results as JSON
    print(json.dumps(results, indent=2))