from defines.defines import getCreds, makeApiCall
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

def search_accounts(usernames, params, output_json_file):
    profiles = []
    already_searched = []
    not_found = []
    for username in usernames:
        print(f"Searching for {username}")
        if verify_username(username, already_searched):
            response = getAccountInfo(username, params)
            if 'error' in response['json_data']:
                print(f"Error: {response['json_data']['error']['message']}")
                not_found.append(username)
                continue
            profile = response['json_data']['business_discovery']
            profiles.append(profile)
            save_profile_info_json(profile, output_json_file)            
        already_searched.append(username)
    return not_found


def verify_username(username, already_searched):
    if username == "explore" or username == "reel" or username in already_searched:
        return False
    return True

def main():
    input_csv_file = 'src/data/input/input.csv'
    output_json_file = 'src/data/output/output.json'
    params = getCreds()
    usernames = get_usernames_from_csv(input_csv_file)
    not_found_usernames = search_accounts(usernames, params, output_json_file)
    
    print(f"Usernames not found: {not_found_usernames}")

if __name__ == '__main__':
    main()
