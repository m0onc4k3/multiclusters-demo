import unittest

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi 

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

def test_subscription_flow():
    # Configure headless options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver (geckodriver should be in PATH)
    driver = webdriver.Firefox(options=options)
    
    try:
        # Test login page
        driver.get("http://localhost:8000/login/")
        print("Page title:", driver.title)
        
        # Fill login form
        username = driver.find_element(By.ID, "id_username")
        password = driver.find_element(By.ID, "id_password")
        # submit = driver.find_element(By.XPATH, "//button[@type='submit']")
        # submit = driver.find_element(By.XPATH, "//form//button[contains(text(),'Login')]")
        submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")  # Update
        
        username.send_keys("testuser")
        password.send_keys("testpass13")
        submit.click()

        # # Verification
        # WebDriverWait(driver, 10).until(
        #     lambda d: "/login/" in d.current_url,
        #     "Page should remain on login after invalid credentials"
        # )
        
        # error = WebDriverWait(driver, 10).until(
        #     EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.errorlist li")),
        #     "Error message should appear"
        # )
        
        # assert "Invalid username or password" in error.text
        # print("✔️ Negative test passed - correctly prevented login")
        
        # Verify login success
        sleep(2)  # Allow page to load
        
        print("Current URL after login:", driver.current_url)
        # Verify successful navigation to address page
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "h2"),
                "Enter the address where we can deliver your magazine"
            )
        )
        print("Successfully reached address entry page")
        
        # Continue with address entry test...
        
    except Exception as e:
        driver.save_screenshot("errors/error.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    test_subscription_flow()