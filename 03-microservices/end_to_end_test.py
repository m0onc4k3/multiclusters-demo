import unittest

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

import os
from time import sleep

class SubscriptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = Options()
        cls.options.add_argument("--headless")
        # cls.options.add_argument("--no-sandbox")
        # cls.options.add_argument("--disable-dev-shm-usage")
        # cls.driver = webdriver.Firefox(options=cls.options)
        cls.base_url = "http://localhost:8000"


    def setUp(self):
        # Runs before each test
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.get(f"{self.base_url}/login/")
        self.debug_screenshots = [] # Store screenshot paths for debugging

    def tearDown(self):
        # Cleanup after each test
        if hasattr(self, '_outcome'): # Python 3.4+
            # Capture screenshot if test failed
            # result = self._outcome.result
            if any(error for (method, error) in self._outcome.result.errors + self._outcome.result.failures):
                screenshot_path = f"errors/failure_{self.id()}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"\nScreenshot saved to: {os.path.abspath(screenshot_path)}")
        self.driver.quit()

    def debug_capture(self, name):
        """Helper method to capture screenshots during tests"""
        path = f"errors/debug_{name}.png"
        self.driver.save_screenshot(path)
        self.debug_screenshots.append(path)
        return path

    def test_invalid_login(self):
        """Test failed login scenario"""
        wronguser = 'testuser'
        wrongpassword = 'testpass'
        try:
            # Enter invalid credentials
            self.driver.find_element(By.ID, 'id_username').send_keys(wronguser)
            self.driver.find_element(By.ID, 'id_password').send_keys(wrongpassword)
            self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

            # Verification
            WebDriverWait(self.driver, 10).until(
                lambda d: "/login/" in d.current_url,
                "Page should remain on login after invalid credentials"
            )

            error = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.errorlist li")),
                "Error message should appear"
            )

            self.assertIn("Invalid username or password", error.text)
            print("✔️  Negative test passed - correctly prevented login")
        except Exception as e:
            self.debug_capture("invalid_login_failure")
            raise



    def test_successful_login_and_form_access(self):
        """Test successful login and form access"""

        try:
            # Enter valid credentials
            self.driver.find_element(By.ID, "id_username").send_keys('testuser')
            self.driver.find_element(By.ID, "id_password").send_keys('testpass123')
            self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            
            # Verify successful navigation to address page
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element(
                    (By.TAG_NAME, "h2"),
                    "Enter the address where we can deliver your magazine"
                )
            )
            print("\n✔️  Successfully reached address entry page")
            
            # Continue with address entry test...
            
        except Exception as e:
            self.debug_capture("successful_login_failure")
            raise

    def test_successful_login_and_form_submission(self):
        """Test successful login and form submission"""

        try:
            # Enter valid credentials
            self.driver.find_element(By.ID, "id_username").send_keys('testuser')
            self.driver.find_element(By.ID, "id_password").send_keys('testpass123')
            self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            
            # Verify successful navigation to address page
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element(
                    (By.TAG_NAME, "h2"),
                    "Enter the address where we can deliver your magazine"
                )
            )
            # print("\n✔️ Successfully reached address entry page")
            
            # Continue with address entry test...
            self.driver.find_element(By.ID, "id_name").send_keys('Carlos Baleba')
            self.driver.find_element(By.ID, "id_address").send_keys('60 Mash Barn Ln')
            self.driver.find_element(By.ID, "id_postalcode").send_keys('BN15 9FP')
            self.driver.find_element(By.ID, "id_city").send_keys('Lancing')
            self.driver.find_element(By.ID, "id_country").send_keys('England')
            self.driver.find_element(By.ID, "id_email").send_keys('cbaleba@brighton.com')
            self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Subscribe']").click()

            # Verify successful navigation to address page
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element(
                    (By.TAG_NAME, "h1"),
                    "Thanks!"
                )
            )
            print("\n✔️  Successfully completed full subscription flow")
            
        except Exception as e:
            self.debug_capture("full_submission_failure")
            raise

if __name__ == "__main__":
    unittest.main()