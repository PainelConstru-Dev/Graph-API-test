from dotenv import load_dotenv
from save_load import save_profile_info_json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import random
import re
import os
import time

def navigator_initializer():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Firefox(options=options)

def instagram_login(browser):
    load_dotenv("src/defines/.env")
    USERNAME = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    browser.get("https://www.instagram.com/")
    try:
        time.sleep(1)
        username = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        username.send_keys(USERNAME)

        time.sleep(2)
        password = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        password.send_keys(PASSWORD)

        time.sleep(1)
        login = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login.click()
        time.sleep(3)   
        not_now = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @tabindex='0' and contains(text(), 'Not Now')]")))
        not_now.click()
        print("Login successful.")
    except:
        print("Login error.")
    
def search_links_selenium(browser, username):
    browser.get(f"https://www.instagram.com/{username}/")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    links = collect_links(browser)
    return links

def search_accounts_selenium(browser, profiles, output_selenium):
    for profile in profiles:
        username = profile['username']
        print(f"Searching for {username}")
        if search_user(browser, username):
            if profile['business_account'] == 'true':
                continue
            biography = collect_biography(browser)
            link_urls = collect_links(browser)
            posts = collect_posts(browser)
            profile_info = {
                "username": username,
                "biography": biography, 
                "links": link_urls, 
                "media_count": len(posts),
                "media": posts
                }
            save_profile_info_json(profile_info, output_selenium)
        else:
            continue

def search_user(browser, username):
    time.sleep(random.randint(1, 3))
    browser.get(f"https://www.instagram.com/{username}/")
    try:
        invalid_Username = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Esta página não está disponível')]"))
        )
        print("User not found.")
        return False
    except:
        pass
    try:
        private_account = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Essa conta é privada')]"))
        )
        print("User account is private.")
        return False
    except:
        return True

def collect_biography(browser):
    try:
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='button' and contains(., 'mais')]//span[@dir='auto']"))).click()
        except:
            pass
        return WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='button']//span[@dir='auto']"))
        ).text
    except:
        return ""
        
def collect_links(browser):
    link_urls = []
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Link icon']"))
        ).click()
        links = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@rel='me nofollow noopener noreferrer']")))
        for link in links:
            href = link.get_attribute("href")
            if href:
                link_urls.append(href)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']"))
        ).click()
    except:
        try:
            links = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@rel='me nofollow noopener noreferrer']"))
            ).text
            link_urls.append(links)
        except:
            pass
    return link_urls

def collect_posts(browser):
    posts, posts_src = [], []
    altura_atual = browser.execute_script("return document.body.scrollHeight")
    while True:
        try:
            posts_elements = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@style, 'display: flex; flex-direction: column;')]//img[@alt and @crossorigin and @style and @src]"))
            )
            for post in posts_elements:
                src = post.get_attribute("src")
                description = post.get_attribute("alt")
                if description and src not in posts_src:
                    posts_src.append(src)
                    date = collect_post_date(description)
                    if description and date and len(posts) < 10:
                        posts.append({"date": str(date), "caption": str(description)})
                    else:
                        continue
        except:
            pass
        browser.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(random.randint(2, 3))
        altura_nova = browser.execute_script("return document.body.scrollHeight")
        if altura_nova == altura_atual:
            break
        altura_atual = altura_nova
    return posts

def collect_post_date(description):
    date_pattern = re.search(r'on (\w+ \d{1,2}, \d{4})', description)
    return date_pattern.group(1) if date_pattern else "Unknown"