import os
import json
import pandas

def get_usernames_from_csv(input_csv_file):
    with open(input_csv_file, "r", encoding="utf-8") as file:
        search_info = pandas.read_csv(file)
    urls = search_info["URL"].tolist()
    usernames = [] 
    for url in urls:
        if "https://www.instagram.com/" in url:
            username = url.split("https://www.instagram.com/")[1].split("/")[0]
            usernames.append(username)
    return usernames

def save_profile_info_json(profiles, output_json_file):
    existing_data = []
    os.makedirs(os.path.dirname(output_json_file), exist_ok=True)
    if os.path.exists(output_json_file) and os.path.getsize(output_json_file) > 0:
        with open(output_json_file, "r", encoding="utf-8") as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    if isinstance(profiles, list):
        existing_data.extend(profiles)
    else:
        existing_data.append(profiles)
    with open(output_json_file, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)