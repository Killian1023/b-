from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import os
from selenium.webdriver.common.action_chains import ActionChains

def save_login_session(url, driver_path, cookies_path):
    driver = webdriver.Chrome(driver_path)
    driver.get(url)

    input("Log in on the browser and then press Enter here...")

    # Save cookies after login
    pickle.dump(driver.get_cookies(), open(cookies_path, "wb"))

    return driver  # Return the driver instance for further use

def send_message_to_chatbot(driver, input_selector, button_selector, cookies_path):
    # Load previously saved cookies
    if os.path.exists(cookies_path):
        cookies = pickle.load(open(cookies_path, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

    # Refresh the page to apply cookies
    driver.refresh()

    try:
        while True:
            # Wait for the input element to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, input_selector)))
            message = input("Enter your message (type 'exit' to close): ")

            if message.lower() == 'exit':
                break

            # Find and send keys to the input element
            input_element = driver.find_element(By.CSS_SELECTOR, input_selector)
            input_element.send_keys(message)

            # Wait for the send button to become clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
            
            # Find the send button
            send_button = driver.find_element(By.CSS_SELECTOR, button_selector)

            # Optional: Scroll to the button
            actions = ActionChains(driver)
            actions.move_to_element(send_button).perform()

            # Click the button
            send_button.click()

    finally:
        driver.quit()


# Set the path for cookies
cookies_path = "/Users/kiwi/Desktop/selenium_cookie/cookies.pkl"

# Save the login session and keep the browser open
driver = save_login_session("https://chat.kiwi-tech.cn", "/Users/kiwi/Downloads/chromedriver-mac-x64/chromedriver", cookies_path)

# Use the same driver instance to send messages
send_message_to_chatbot(driver, ".chat_chat-input__PQ_oF", ".chat_chat-input-send__GFQZo", cookies_path)
