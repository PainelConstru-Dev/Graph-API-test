from dotenv import load_dotenv
from save_load import get_usernames_from_csv, save_profile_info_json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
import re

def navigator_initializer():
    return webdriver.Firefox()

def instagram_login(browser):
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
    except:
        print("Login error.")

def ignore_save_login(browser):
    try:
        time.sleep(3)   
        not_now = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @tabindex='0' and contains(text(), 'Agora não')]")))
        not_now.click()
    except:
        print("Error clicking in not now button.")

def search_users(browser, usernames, output_json_file):
    instagram_login(browser)
    ignore_save_login(browser)
    for username in usernames:
        if verify_username(browser, username):
            if search_user(browser, username):
                biography = collect_biography(browser)
                link_urls = collect_links(browser)
                posts = collect_posts(browser)
                profile_info = {"Username": username, "Biography": biography, "Links": link_urls, "Posts": posts}
                save_profile_info_json(profile_info, output_json_file)
                print(f"The profile information of {username} has been saved.")
            else:
                continue

def search_user(browser, username):
    try:
        time.sleep(random.randint(1, 3))
        browser.get(f"https://www.instagram.com/{username}/")
    except:
        print("Error searching Username.")
        return False
    try:
        invalid_Username = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Esta página não está disponível')]"))
        )
        print("User not found.")
        return False
    except:
        print("User found.")
        pass
    try:
        private_account = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Essa conta é privada')]"))
        )
        print("User account is private.")
        return False
    except:
        print("User account is public.")
        return True

def verify_username(browser, username):
    if username == "explore" or username == "reel":
        return False
    return True

def collect_biography(browser):
    try:
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='button' and contains(., 'mais')]//span[@dir='auto']"))).click()
        except:
            print("Error clicking in more button.")
            pass
        return WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='button']//span[@dir='auto']"))
        ).text
    except:
        print("Error collecting biography.")
        return ""
        
def collect_links(browser):
    link_urls = []
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Ícone de link']"))
        ).click()
        links = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@rel='me nofollow noopener noreferrer']")))
        for link in links:
            href = link.get_attribute("href")
            if href:
                link_urls.append(href)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Fechar']"))
        ).click()
    except:
        try:
            links = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@rel='me nofollow noopener noreferrer']"))
            ).text
            link_urls.append(links)
        except:
            print("Error collecting links.")
            pass
    return link_urls

def collect_posts(browser):
    posts, posts_src = [], []
    altura_atual = browser.execute_script("return document.body.scrollHeight")
    count = 0
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
                    if description and date:
                        posts.append({"description": str(description), "date": str(date)})
                        count += 1
                    else:
                        print("No new posts.")
            print(f"Post {count}")
        except:
            print("Error collecting posts.")
        
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

def main():
    load_dotenv("src/defines/.env")
    input_csv_file = "src/input/input.csv"
    output_json_file = "src/output/outputSelenium.json"
    usernames = get_usernames_from_csv(input_csv_file)
    browser = navigator_initializer()
    search_users(browser, usernames, output_json_file)
    browser.quit()

if __name__ == "__main__":
    main()