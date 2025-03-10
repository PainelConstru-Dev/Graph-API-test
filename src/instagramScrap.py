from defines.defines import getCreds, makeApiCall
import pandas
import json
import os

def getAccountInfo(username, params):
	""" Get info on a users account
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

	Returns:
		object: data from the endpoint
    """
	params['ig_username'] = username; params['debug'] = 'no' # set debug
	endpointParams = dict() # parameter to send to the endpoint
	#endpointParams['fields'] = 'business_discovery.username(' + params['ig_username'] + '){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count,media.limit(1000){caption,comments_count,like_count,media_product_type,media_url,thumbnail_url,timestamp,permalink}}' # string of fields to get back with the request for the account
	endpointParams['fields'] = 'business_discovery.username(' + params['ig_username'] + '){username,name,follows_count,followers_count,media_count,biography,website,profile_picture_url,media.limit(1000){timestamp,like_count,comments_count,caption}}' # string of fields to get back with the request for the account
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def search_accounts(usernames, params, output_json_file):
    profiles = []
    for username in usernames:
        print(f"Searching for {username}")
        if verify_username(username):
            response = getAccountInfo(username, params)
            if 'error' in response['json_data']:
                print(f"Error: {response['json_data']['error']['message']}")
                continue
            profile = response['json_data']['business_discovery']
            profiles.append(profile)
            save_profile_info_json(profile, output_json_file)

def verify_username(username):
    if username == "explore" or username == "reel":
        return False
    return True

def get_usernames_from_csv(input_csv_file):
    os.makedirs(os.path.dirname(input_csv_file), exist_ok=True)
    with open(input_csv_file, "r", encoding="utf-8") as file:
        search_info = pandas.read_csv(file)
    urls = search_info["URL"].tolist()
    usernames = [] 
    for url in urls:
        if "https://www.instagram.com/" in url:
            username = url.split("https://www.instagram.com/")[1].split("/")[0]
            usernames.append(username)
    return usernames

def save_profile_info_json(profile, output_json_file):
    existing_data = []
    if os.path.exists(output_json_file) and os.path.getsize(output_json_file) > 0:
        with open(output_json_file, "r", encoding="utf-8") as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    if isinstance(profile, list):
        existing_data.extend(profile)
    else:
        existing_data.append(profile)

    with open(output_json_file, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

def main():
    input_csv_file = 'src/input/input.csv'
    output_json_file = 'src/output/output.json'
    params = getCreds()
    usernames = get_usernames_from_csv(input_csv_file)
    search_accounts(usernames, params, output_json_file)

if __name__ == '__main__':
    main()
