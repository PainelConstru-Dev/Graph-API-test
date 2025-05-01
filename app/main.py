import sys
from defines import getCreds
from save_load import get_usernames_from_csv
from instagramScrapSelenium import *
from instagramScrapGraphAPI import *

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_csv_path>")
        return

    input_csv_file = sys.argv[1]
    output_file = input_csv_file.replace("parts", "output").replace(".csv", "_results.json")
    print(f"Input CSV file: {input_csv_file}")
    params = getCreds()
    usernames = get_usernames_from_csv(input_csv_file)
    browser = navigator_initializer()
    instagram_login(browser)
    profiles = search_accounts(browser, usernames, params, output_file)
    search_accounts_selenium(browser, profiles, output_file)
    browser.quit()

if __name__ == '__main__':
    main()