"""
Shows basic usage of the Photos v1 API.
Creates a Photos v1 API service and prints the names and ids of the last 10 albums
the user has access to.
"""
#from __future__ import print_function
import os 
import pickle
#import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_httplib2  # This gotta be installed for build() to work
import time
# Setup the Photo v1 API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
creds = None
if(os.path.exists("token.pickle")):
    with open("token.pickle", "rb") as tokenFile:
        creds = pickle.load(tokenFile)
if not creds or not creds.valid:
    if (creds and creds.expired and creds.refresh_token):
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port = 0)
    with open("token.pickle", "wb") as tokenFile:
        pickle.dump(creds, tokenFile)
service = build('photoslibrary', 'v1', credentials = creds)

f=open("google_image_list_2.txt","w",encoding='utf-8')
# Call the Photo v1 API
page_token = None
max_errors=5
num_errors=0
while True:
    try:
        results = service.mediaItems().list(pageSize=100, fields="nextPageToken,mediaItems(id,filename)", pageToken=page_token).execute()
        page_token = results.get('nextPageToken', None)
        items = results.get('mediaItems', [])
        print(len(items))
        if not items:
            print('No files found.')
        else:
            for item in items:
                f.write('{0},{1}\n'.format(item['filename'],item['id']))
        if not page_token:
            # no more files
            break
        f.flush()
        num_errors=0
    except HttpError as e:
        print(e)
        time.sleep(1)
        num_errors = num_errors +1
        if num_errors > max_errors:
            break

print("---------------------")
f.close()
#results = service.albums().list(
#    pageSize=10, fields="nextPageToken,albums(id,title)").execute()
#items = results.get('albums', [])
#if not items:
#    print('No albums found.')
#else:
#    print('Albums:')
#    for item in items:
#        print('{0} ({1})'.format(item['title'].encode('utf8'), item['id']))

