from defines import makeApiCall
from instagramScrapSelenium import *
from save_load import save_profile_info_json

def getAccountInfo(username, params):
	""" Get info on a users account
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

	Returns:
		object: data from the endpoint
    """
	params['debug'] = 'no' # set debug
	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'business_discovery.username(' + username + '){username,name,follows_count,followers_count,media_count,biography,website,profile_picture_url,media.limit(3999){timestamp,like_count,comments_count,caption}}' # string of fields to get back with the request for the account
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def search_accounts(browser, usernames, params, output_json_file):
    profiles = []
    already_searched = []
    accounts = [
        {
            'access_token': params['access_token'],
            'instagram_account_id': params['instagram_account_id']
        },
        {
            'access_token': params['access_token2'],
            'instagram_account_id': params['instagram_account_id2']
        },
        {
            'access_token': params['access_token3'],
            'instagram_account_id': params['instagram_account_id3']
        }
    ]
    
    for username, cnpj in usernames:
        print(f"Searching for {username}")

        if verify_username(username, already_searched):
            success = False
            
            while not success:
                for account in accounts:
                    params['access_token'] = account['access_token']
                    params['instagram_account_id'] = account['instagram_account_id']
                    response = getAccountInfo(username, params)
                    if 'error' in response['json_data']:
                        message = response['json_data']['error']['message']
                        if message == "(#4) Application request limit reached":
                            print("Limit reached. Switching account.")
                            continue
                        else:
                            success = True
                            print("Error:", message)
                            profiles.append({"username": username, "cnpj": cnpj, "business_account": 'false'})
                            save_profile_info_json({"username": username, "business_account": 'false'}, output_json_file)
                            break
                    else:
                        success = True
                        links = search_links_selenium(browser, username)
                        profile = save_profile(username, cnpj, response, links)
                        profiles.append(profile)
                        save_profile_info_json(profile, output_json_file)
                        already_searched.append(username)
                        break
                if not success:
                    print("Error occurred. Retrying in 1 hour...")
                    time.sleep(3600)
    return profiles

def verify_username(username, already_searched):
    if username == "explore" or username == "reel" or username == "p" or username in already_searched:
        print(f"Invalid user id.")
        return False
    return True

def save_profile(username, cnpj, response, links):
    business_discovery = response.get('json_data', {}).get('business_discovery', {})
    name = business_discovery.get('name')
    follows_count = business_discovery.get('follows_count')
    followers_count = business_discovery.get('followers_count')
    media_count = business_discovery.get('media_count')
    biography = business_discovery.get('biography')
    profile_picture_url = business_discovery.get('profile_picture_url')
    media = business_discovery.get('media', {}).get('data', [])
    profile = {
        "cnpj": cnpj,
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