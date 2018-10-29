#!/usr/bin/env python

import json
import sys
import requests
from pprint import pprint
#Surpress HTTPS insecure errors for cleaner output
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

FMC_USER = "apiuser"
FMC_PASSWORD = "C1sc0123"
FMC_HOST = "10.19.66.126"
FMC_PORT = "40003"

def get_auth_token(host=FMC_HOST, username=FMC_USER, password=FMC_PASSWORD):
	""" 
	Authenticates with FMC and returns a token to be used in subsequent API calls
	"""
	headers = {'Content-Type': 'application/json'}
	login_url = "https://{0}:{1}/api/fmc_platform/v1/auth/generatetoken".format(host,FMC_PORT)

	result = requests.post(url=login_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
	result.raise_for_status()
	auth_headers = result.headers
	token = auth_headers.get('X-auth-access-token', default=None)
	uuid = auth_headers.get('DOMAIN_UUID', default=None)
	headers['X-auth-access-token'] = token

	return headers,uuid
	
def create_url(path, uuid, host=FMC_HOST):
    """ Helper function to create an FMC API endpoint URL
    """
    return "https://%s:%s/api/fmc_config/v1/domain/%s/%s" % (host, FMC_PORT, uuid, path)

def get_url(url):

    headers,uuid = get_auth_token()
    url = create_url(path=url,uuid=uuid)
    print(url)
    
    try:
        response = requests.get(url, headers=headers, verify=False)
    except requests.exceptions.RequestException as err:
        print("Error processing request", err)
        sys.exit(1)

    return response.json()

def post_url(url,data):

    headers,uuid = get_auth_token()
    url = create_url(path=url,uuid=uuid)
    print(url)

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
        status_code = response.status_code
        print("status code is: " + str(status_code))
        if status_code == 201 or status_code == 202:
            print("Post was sucessfull...")
        else:
            response.raise_for_status()
            print("error occured in POST -->" + response.text)
        return response.json()
    except requests.exceptions.HTTPError as err:
        print("Error in connection --> " + str(err))
    finally:
        if response:
            response.close()
		
if __name__ == "__main__":

    headers,uuid = get_auth_token()
    print("Successfully authenticated to FMC\nReceived Auth Token: {0}\nDomain ID: {1}".format(headers['X-auth-access-token'],uuid))

    url = "policy/accesspolicies"
    data = {
              "type": "AccessPolicy",
              "name": "DNE Security Access Control Policy",
              "description": "Basic AC Policy",
              "defaultAction": {
              "action": "BLOCK"
              }
            }
    acp = post_url(url,data)
    pprint(acp)