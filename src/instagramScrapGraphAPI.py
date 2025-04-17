from defines.defines import getCreds, makeApiCall
from instagramScrapSelenium import *
from save_load import get_usernames_from_csv, save_profile_info_json

def getAccountInfo(username, params):
	""" Get info on a users account
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

	Returns:
		object: data from the endpoint
    """
	params['debug'] = 'no' # set debug
	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'business_discovery.username(' + username + '){username,name,follows_count,followers_count,media_count,biography,website,profile_picture_url,media.limit(2000){timestamp,like_count,comments_count,caption}}' # string of fields to get back with the request for the account
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def search_accounts(browser, usernames, params, output_json_file):
    profiles = []
    already_searched = []
    usernames = ["painelconstru"]
    for username in usernames:
        print(f"Searching for {username}")
        if verify_username(username, already_searched):
            response = getAccountInfo(username, params)
            if 'error' in response['json_data']:
                message = response['json_data']['error']['message']
                if message == "(#4) Application request limit reached":
                    print("Application request limit reached.")
                    time.sleep(3600)
                    response = getAccountInfo(username, params)
                else:
                    print(message)
                    profiles.append({"username": username, "business_account": 'false'})
                    continue
            links = search_links_selenium(browser, username)
            profile = save_profile(username, response, links)
            profiles.append(profile)
            save_profile_info_json(profile, output_json_file)           
            already_searched.append(username)
    return profiles

def verify_username(username, already_searched):
    if username == "explore" or username == "reel" or username == "p" or username in already_searched:
        print(f"Invalid user id.")
        return False
    return True

def save_profile(username, response, links):
    business_discovery = response.get('json_data', {}).get('business_discovery', {})
    name = business_discovery.get('name')
    follows_count = business_discovery.get('follows_count')
    followers_count = business_discovery.get('followers_count')
    media_count = business_discovery.get('media_count')
    biography = business_discovery.get('biography')
    profile_picture_url = business_discovery.get('profile_picture_url')
    media = business_discovery.get('media', {}).get('data', [])
    profile = {
        "username": username,
        "name": name,
        "business_account": 'true',
        "follows_count": follows_count,
        "followers_count": followers_count,
        "media_count": media_count,
        "biography": biography,
        "links": links,
        "profile_picture_url": profile_picture_url,
        "media": media
    }
    return profile

def main():
    input_csv_file = 'src/data/input/input.csv'
    input_csv_file_selenium = "src/data/input/input.csv"
    output_graph = 'src/data/output/graphAPI_results.json'
    output_selenium = "src/data/output/selenium_results.json"
    output_graph_selenium = "src/data/output/graphAPI_selenium_results.json"
    params = getCreds()
    usernames = get_usernames_from_csv(input_csv_file)
    browser = navigator_initializer()
    login_instagram(browser)
    profiles = search_accounts(browser, usernames, params, output_graph_selenium)
    search_accounts_selenium(browser, profiles, output_selenium)

    
if __name__ == '__main__':
    main()
