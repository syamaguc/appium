import time
import datetime
import math
import re
import requests
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.appiumby import AppiumBy


def setup_appium():
    desired_caps = dict(
        platformName='Android',
        platformVersion='12',
        automationName='UiAutomator2',
        deviceName='emulator-5554',
        noReset=True,
        # appPackage='com.bcy.fsapp',
    )
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver


def login(driver):
    el = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='STEPN')
    el.click()
    time.sleep(5)


def scroll_down(driver):
    while True:
        scraping(driver)
        scroll_down_helper(driver)
        try:
            elm = driver.find_element(
                by=AppiumBy.XPATH, value="//android.view.View[@content-desc='No more data']")
            break
        except:
            continue


def scroll_down_helper(driver):
    window_height = get_window_height(driver)
    scroll_distance = window_height * 2 / 3  # Here can be more optimized
    TouchAction(driver).long_press(x=300, y=window_height - 250).move_to(
        x=300, y=max(window_height - 250 - scroll_distance, 250)).release().perform()
    # time.sleep(1)


def get_window_height(driver):
    bottom_bar_height = 100  # 56px + additional bottom space
    scale = driver.get_display_density() / 160
    bottom_bar_height = bottom_bar_height * scale
    return driver.get_window_size()['height'] - bottom_bar_height


def open_market(driver):
    el = driver.find_element(by=AppiumBy.XPATH,
                             value="/ hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[5]")
    el.click()


def print_progress():
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")}')


def scraping(driver):
    els = driver.find_elements(
        by=AppiumBy.XPATH, value="//*[starts-with(@content-desc,'100')]")
    for el in els:
        print("-------------------------------\n")
        print(el.get_attribute('content-desc'))
        print("\n")


if __name__ == "__main__":
    start = time.time()
    print('Start: ' + datetime.datetime.now().strftime('%H:%M:%S'))
    driver = setup_appium()
    login(driver)
    open_market(driver)
    scroll_down(driver)
