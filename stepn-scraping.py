import time
import datetime
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.appiumby import AppiumBy
from google.oauth2 import service_account
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import sys


arguments = sys.argv
scopes = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    'service-account-credentials.json', scopes=scopes)

if arguments[1] == "shoes":
    df = [['type', '', 'ID', 'mint', 'Lv', 'price']]
elif arguments[1] == "gem":
    df = [['ID', 'price', 'Lv', 'mint']]


def setup_appium():
    desired_caps = dict(
        platformName='Android',
        platformVersion='12',
        automationName='UiAutomator2',
        deviceName='emulator-5554',
        noReset=True,
    )
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver


def login(driver):
    el = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='STEPN')
    el.click()
    time.sleep(5)
    el = driver.find_element(by=AppiumBy.XPATH,
                             value="/ hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[5]")
    el.click()


def filter(driver):
    if arguments[1] == "shoes":
        el = driver.find_element(
            by=AppiumBy.XPATH, value="/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[2]/android.view.View/android.view.View/android.widget.ImageView[2]")
        el.click()
        time.sleep(2)
        el = driver.find_element(
            by=AppiumBy.ACCESSIBILITY_ID, value='Sneakers')
        el.click()
        time.sleep(2)
        el = driver.find_element(
            by=AppiumBy.ACCESSIBILITY_ID, value='CONFIRM')
        el.click()
        time.sleep(2)
    elif arguments[1] == "gem":
        el = driver.find_element(
            by=AppiumBy.ACCESSIBILITY_ID, value='Gems')
        el.click()
        time.sleep(2)
    else:
        pass


def scroll_down_loop(driver):
    window_height = get_window_height(driver)
    scroll_distance = window_height * 2 / 3  # Here can be more optimized
    # for i in range(5): -> test
    while True:
        scraping(driver)
        TouchAction(driver).long_press(x=300, y=window_height - 250).move_to(
            x=300, y=max(window_height - 250 - scroll_distance, 250)).release().perform()
        try:
            elm = driver.find_element(
                by=AppiumBy.XPATH, value="//android.view.View[@content-desc='No more data']")
            break
        except:
            continue


def get_window_height(driver):
    bottom_bar_height = 100  # 56px + additional bottom space
    scale = driver.get_display_density() / 160
    bottom_bar_height = bottom_bar_height * scale
    return driver.get_window_size()['height'] - bottom_bar_height


def open_market(driver):
    el = driver.find_element(by=AppiumBy.XPATH,
                             value="/ hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[5]")
    el.click()
    time.sleep(2)
    filter(driver)


def print_progress():
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")}')


def scraping(driver):
    global df
    if arguments[1] == "shoes":
        els = driver.find_elements(
            by=AppiumBy.XPATH, value="//*[starts-with(@content-desc,'100')]")
    elif arguments[1] == "gem":
        els = driver.find_elements(
            by=AppiumBy.XPATH, value="//*[starts-with(@content-desc,'#')]")
    for el in els:
        df.append(list(el.get_attribute('content-desc').split('\n')))


def update_ss(df):
    df = pd.DataFrame(df)
    df = df.drop_duplicates()
    gc = gspread.authorize(credentials)
    wb = gc.open_by_key('1-qTgzHxuVysoq-XIIbB7WdsDjRfjEYBzKrAydjZRDcs')
    if arguments[1] == "shoes":
        ws = wb.worksheet('db_shoes')
    elif arguments[1] == "gem":
        ws = wb.worksheet('db_gem')
    ws.clear()
    set_with_dataframe(ws, df)


if __name__ == "__main__":
    if len(arguments) == 2 and arguments[1] in ['shoes', 'gem']:
        print('Start: ' + datetime.datetime.now().strftime('%H:%M:%S'))
        driver = setup_appium()
        login(driver)
        open_market(driver)
        scroll_down_loop(driver)
        update_ss(df)
        driver.close_app()
        print('End: ' + datetime.datetime.now().strftime('%H:%M:%S'))
    else:
        print("Usage: stepn-scraping.py [shoes/gem]")
