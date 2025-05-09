import os
import json
import pandas

def get_usernames_from_csv(input_csv_file):
    try:
        search_info = pandas.read_csv(input_csv_file, encoding="utf-8")
    except pandas.errors.ParserError:
        search_info = pandas.read_csv(input_csv_file, encoding="ISO-8859-1")

    usernames = []
    for _, row in search_info.iterrows():
        url = str(row["contato"])
        if "https://www.instagram.com/" in url:
            username = url.split("https://www.instagram.com/")[1].split("/")[0]
            cnpj_basico = str(row["cnpj_basico"]).zfill(8)
            cnpj_ordem = str(row["cnpj_ordem"]).zfill(4)
            cnpj_dv = str(row["cnpj_dv"]).zfill(2)
            cnpj = f"{cnpj_basico[:2]}.{cnpj_basico[2:5]}.{cnpj_basico[5:]}/{cnpj_ordem}-{cnpj_dv}"
            usernames.append((username, cnpj))
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