import requests
import json
from dotenv import load_dotenv
import os

def getCreds() :
	""" Get creds required for use in the applications
	
	Returns:
		dictonary: credentials needed globally

	"""
	load_dotenv()
	creds = dict() # dictionary to hold everything
	creds['access_token'] = os.getenv('ACCESS_TOKEN') # access token for use with all api calls
	creds['access_token2'] = os.getenv('ACCESS_TOKEN2') # access token for use with all api calls
	creds['access_token3'] = os.getenv('ACCESS_TOKEN3') # access token for use with all api calls
	creds['client_id'] = os.getenv('CLIENT_ID') # client id from facebook app IG Graph API Test
	creds['client_secret'] = os.getenv('CLIENT_SECRET') # client secret from facebook app
	creds['facebook_page_id'] = os.getenv('FACEBOOK_PAGE_ID') # users facebook page id
	creds['instagram_account_id'] = os.getenv('INSTAGRAM_ACCOUNT_ID') # users instagram account id
	creds['instagram_account_id2'] = os.getenv('INSTAGRAM_ACCOUNT_ID2') # users instagram account id
	creds['instagram_account_id3'] = os.getenv('INSTAGRAM_ACCOUNT_ID3') # users instagram account id
	creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
	creds['graph_version'] = 'v22.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
	creds['debug'] = 'no' # debug mode for api call

	return creds

def makeApiCall( url, endpointParams, debug = 'no' ) :
	""" Request data from endpoint with params
	
	Args:
		url: string of the url endpoint to make request from
		endpointParams: dictionary keyed by the names of the url parameters


	Returns:
		object: data from the endpoint

	"""

	data = requests.get( url, endpointParams ) # make get request

	response = dict() # hold response info
	response['url'] = url # url we are hitting
	response['endpoint_params'] = endpointParams #parameters for the endpoint
	response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
	response['json_data'] = json.loads( data.content ) # response data from the api
	response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

	if ( 'yes' == debug ) : # display out response info
		displayApiCallData( response ) # display response

	return response # get and return content

def displayApiCallData( response ) :

	print ("\nURL: ") # title
	print (response['url']) # display url hit
	print ("\nEndpoint Params: ") # title
	print (response['endpoint_params_pretty']) # display params passed to the endpoint
	print ("\nResponse: ") # title
	print (response['json_data_pretty']) # make look pretty for cli