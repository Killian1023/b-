import asyncio
import http.cookies
import aiohttp
import blivedm
import blivedm.models.web as web_models
from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import os
from selenium.common.exceptions import NoSuchElementException
import time

# Bilibili live stream settings
TEST_ROOM_IDS = [10120377]  # 更改为我们的直播间ID
SESSDATA = ''  # Replace with your SESSDATA if needed

# Selenium settings
CHATBOT_URL = "https://chat.kiwi-tech.cn"  # Replace with the chatbot URL
DRIVER_PATH = "/Users/kiwi/Downloads/chromedriver-mac-x64/chromedriver"  # 更改为chromedriver的路径
COOKIES_PATH = "/Users/kiwi/Desktop/selenium_cookie/cookies.pkl"  # 更改为cookies的路径，如果没有就创建一个空文件夹
INPUT_SELECTOR = ".chat_chat-input__PQ_oF"  # Replace with the correct input selector
BUTTON_SELECTOR = ".chat_chat-input-send__GFQZo"  # Replace with the correct button selector
status_selector = ".chat_chat-message-status__zc9Ad" 

# Global variables
session = None
driver = None


async def main():
    global driver
    driver = save_login_session(CHATBOT_URL, DRIVER_PATH, COOKIES_PATH)

    init_session()
    try:
        await run_single_client()
    finally:
        await session.close()
        driver.quit()


def init_session():
    global session
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = SESSDATA
    cookies['SESSDATA']['domain'] = 'bilibili.com'
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client():
    room_id = TEST_ROOM_IDS[0]  # Use the first room ID for demo
    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler(driver, INPUT_SELECTOR, BUTTON_SELECTOR, status_selector)
    client.set_handler(handler)
    client.start()

    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    def __init__(self, driver, input_selector, button_selector, status_selector):
        self.driver = driver
        self.input_selector = input_selector
        self.button_selector = button_selector
        self.status_selector = status_selector

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        if message.msg.startswith("//"):
            self.send_message_to_chatbot(message.msg[2:])
        
    def send_message_to_chatbot(self, message):
        # Wait until the chatbot is ready to receive a message
        while True:
            try:
                self.driver.find_element(By.CSS_SELECTOR, self.status_selector)
                print("Waiting for chatbot to respond...")
                time.sleep(2)
            except NoSuchElementException:
                break

        input_element = self.driver.find_element(By.CSS_SELECTOR, self.input_selector)
        input_element.send_keys(message)
        send_button = self.driver.find_element(By.CSS_SELECTOR, self.button_selector)
        send_button.click()


def save_login_session(url, driver_path, cookies_path):
    global driver
    driver = webdriver.Chrome(driver_path)
    driver.get(url)

    input("Log in on the browser and then press Enter here...")
    pickle.dump(driver.get_cookies(), open(cookies_path, "wb"))
    return driver


if __name__ == '__main__':
    asyncio.run(main())
