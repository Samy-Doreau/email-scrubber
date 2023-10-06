from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class UnsubscribeService:
    def __init__(self, target_urls):
        self.target_url = target_url

    def attempt_unsubscribe(self):
        results = {}
        # Use BeautifulSoup to find 'Unsubscribe' links
        # Attempt to unsubscribe if possible

        driver = Chrome()
        driver.get(self.target_url)
        try:
            print("Attempting to unsub .. ", end="", flush=True)

            # Dirtea, healf
            wait = WebDriverWait(driver, 10)
            unsubscribe_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Unsubscribe')]")
                )
            )
            unsubscribe_button.click()

            # unsubscribe_button.click()
            print("Attempt complete. Awaiting confirmation .. ", end="", flush=True)

            # Check for a confirmation message
            # try:
            #     confirmation_element_1 = driver.find_element(
            #         "xpath",
            #         "//*[contains(text(),'no longer subscribed') or contains(text(),'Unsubscribed' or contains(text(),'saved')]",
            #     )
            #     print("Unsubscription confirmed.")
            # except NoSuchElementException:
            #     print("Confirmation message not found")

            # Wait for the new page to load
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )

            # Check if the page loaded properly (this doesn't check the HTTP status but rather if the page is interactive)
            if driver.execute_script("return document.readyState") == "complete":
                print("Unsubscription page loaded successfully.")
                return {"unsub_button_found": True, "unsub_button_functional": True}
            else:
                print("Error loading the unsubscription page.")
                return {"unsub_button_found": True, "unsub_button_functional": False}
        except NoSuchElementException:
            print("Unsubscribe button not found")
            return {"unsub_button_found": False, "unsub_button_functional": None}
