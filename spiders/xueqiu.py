# 雪球

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import etree
import json
import time


def get_driver():
    chrome_exe_path = 'c:\\selenium\\chromedriver.exe'
    chrome_op = webdriver.ChromeOptions()
    # chrome_op.add_argument('--headless')
    chrome_op.add_argument('--disable-gpu')
    chrome_op.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36')

    driver = webdriver.Chrome(executable_path=chrome_exe_path,
                              chrome_options=chrome_op
                              )
    driver.implicitly_wait(10)
    return driver


def close_driver(d):
    try:
        d.quit()
    except Exception as e:
        print(e)


def go_home(driver):
    home_url = 'https://xueqiu.com/'
    driver.get(home_url)


def go_login(driver):
    t = int(time.time() * 1000)
    login_url = f'https://xueqiu.com/snowman/provider/geetest?t={t}&type=login_pwd'
    driver.get(login_url)
    login_content = driver.page_source
    login_dom = etree.HTML(login_content)
    json_str = login_dom.xpath("string(//pre)")
    login_obj = json.loads(json_str)
    return login_obj


def go_check(driver):
    try:
        locator = (By.CLASS_NAME, 'nav__login__btn')
        WebDriverWait(driver, 20, 1).until(EC.element_to_be_clickable(locator))
        driver.find_element_by_class_name('nav__login__btn').click()
    except Exception as e:
        print('1', e)
        close_driver(driver)
    try:
        locator = (By.TAG_NAME, 'input')
        WebDriverWait(driver, 20, 1).until(EC.presence_of_element_located(locator))
        name_input = driver.find_element_by_xpath('//input[@name="username"]')
        name_input.send_keys('123')
        pwd_input = driver.find_element_by_xpath('//input[@name="password"]')
        pwd_input.send_keys('456')
        driver.find_element_by_class_name('modal__login__btn').click()
    except Exception as e:
        print(e)
        close_driver(driver)

    # try:
    #     locator = (By.CLASS_NAME, 'geetest_widget')
    #     WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    # finally:
    #     close_driver(driver)


if __name__ == "__main__":
    try:
        handle = get_driver()
        go_home(handle)
        # login_obj = go_login(handle)
        # print(login_obj)
        go_check(handle)
    finally:
        # close_driver(handle)
        pass
