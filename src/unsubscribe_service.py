from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class UnsubscribeService:
    def __init__(self, target_urls):
        self.target_urls = target_urls

    def attempt_unsubscribe(self):
        # Use BeautifulSoup to find 'Unsubscribe' links
        # Attempt to unsubscribe if possible

        driver = Chrome()
        driver.get(self.target_urls[0])
        try:
            print("Attempting to unsub .. ", end="", flush=True)
            # unsubscribe_button = driver.find_element("xpath", "//input[@type='submit']")
            # unsubscribe_button = driver.find_element(
            #     "xpath", "//button[@type='submit' and text()='Unsubscribe']"
            # )
            wait = WebDriverWait(driver, 10)
            unsubscribe_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Unsubscribe')]")
                )
            )
            unsubscribe_button.click()

            # unsubscribe_button.click()
            print("Attempt complete. Awaiting confirmation .. ", end="", flush=True)

            # Wait for the new page to load
            time.sleep(5)  # Adjust the waiting time as needed

            # Check for a confirmation message
            try:
                confirmation_element_1 = driver.find_element(
                    "xpath",
                    "//*[contains(text(),'no longer subscribed') or contains(text(),'Unsubscribed')]",
                )
                print("Unsubscription confirmed.")
            except NoSuchElementException:
                print("Confirmation message not found")

        except NoSuchElementException:
            print("Unsubscribe button not found")

        # //*[@id="unsub_submit"]
