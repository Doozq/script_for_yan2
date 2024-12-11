import logging
import time
import random
from datetime import datetime

import logger_setup

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_balance(driver):
    try:
        time.sleep(1)
        number_elements = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'number')]//span[contains(@style, 'visibility: visible')]",
        )
        numbers = [i.text for i in number_elements]
        balance = int("".join(numbers))
        return balance

    except Exception as e:
        return 0

def check_tanos(driver):
    try:
        driver.implicitly_wait(0)
        alarm = driver.find_element(By.XPATH, "//*[contains(text(), 'I AM')]")
        driver.implicitly_wait(10)
        time.sleep(random.uniform(9.0, 11.0))

        logging.info("TANOS was dodged in work")
        return True
    
    except NoSuchElementException:
        driver.implicitly_wait(10)
        return False

    except Exception as e:
        logging.error(f"Error in check_tanos: {e}")
        raise

def claim(driver, profile_id, profiles):
    profile_name = profiles[profile_id]["name"]
    try:
        start_balance = get_balance(driver)

        balance_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'button_rjvnl')]/img")
        time.sleep(2)
        check_tanos(driver)

        balance_btn.click()
        time.sleep(1)

        if check_tanos(driver):
            claim(driver, profile_id, profiles)
            return
        claim_btn = driver.find_element(By.XPATH, "//span[text() = 'Claim']")
        claim_btn.click()
        time.sleep(random.uniform(3.0, 5.0))

        if check_tanos(driver):
            claim(driver, profile_id, profiles)
            return
        balance_btn.click()
        time.sleep(3)
        
        check_tanos(driver)
        end_balance = get_balance(driver)
        profit = end_balance - start_balance
        if end_balance:
            profiles[profile_id]["balance"] = end_balance
        if start_balance and end_balance and profit:
            profiles[profile_id]["last_claim"] = datetime.now()

        logging.info(f"Profile {profile_name}. Claim completed. Profit: {profit}, Balance: {end_balance}")

    except NoSuchElementException as e:
        logging.info(f"Profile {profile_name}. Claim is not available yet: {e}")
        balance_btn.click()
        time.sleep(1)

    except Exception as e:
        logging.error(f"Profile {profile_name}. Error in claim: {e}")
        raise
