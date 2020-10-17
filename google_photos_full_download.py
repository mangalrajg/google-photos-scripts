# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 12:05:21 2020

@author: Mangalraj
"""

import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_httplib2  # This gotta be installed for build() to work
import time
import datetime
from dateutil.parser import parse
import os
import shutil
import requests
import concurrent.futures


base_output_dir="google2"
photo_ids_processed="ids_processed.txt"
processed_ids=[]
processed_ids = set(line.strip() for line in open(photo_ids_processed))

 
def process_single(mediaItem):
    base_url = mediaItem["baseUrl"]
    filename = mediaItem["filename"]
    metadata = mediaItem["mediaMetadata"]
    creationTimeStr = metadata["creationTime"]
    photo_id = mediaItem["id"]
    if photo_id in processed_ids:
        print("Already downloaded id")
        return
    else:
        #processed_ids.add(photo_id)
        creationTime = parse(creationTimeStr)            
        path = os.path.join(base_output_dir, f"{str(creationTime.year)}/{str(creationTime.month)}")
        os.makedirs(path, exist_ok = True)
        url_suffix=""
        if "video" in metadata:
            url_suffix="dv"
        else:
            url_suffix="d"
        
        base_url_w_suffix=f"{base_url}={url_suffix}"
        filename_with_path=os.path.join(path,filename)
        if os.path.exists(filename_with_path):
            filename_with_path=os.path.join(path,"Duplicates", filename)
            os.makedirs(os.path.join(path,"Duplicates"),exist_ok = True)
        r = requests.get(base_url_w_suffix, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            print(f"  writing file {filename_with_path}")
            with open(filename_with_path,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                print("*", end="")
                return photo_id
            #print(f'OK {filename} suffix:{url_suffix}')
        else:     
            print(f'    KO {filename} suffix:{url_suffix} status: {r.status_code}:{r.text}')
    
def process_batch(mediaItems):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(process_single, mediaItem): mediaItem for mediaItem in mediaItems}
        for future in concurrent.futures.as_completed(future_to_url):
            mediaItem = future_to_url[future]
            try:
                photo_id = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                if photo_id is not None:
                    id_file = open(photo_ids_processed, "a")
                    id_file.write(photo_id)
                    id_file.write("\n")
                    id_file.close()
                    print(".", end="")
                else:
                    print("#", end="")
            



    
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

page_token = None
max_errors=5
num_errors=0
while True:
    try:
        results = service.mediaItems().list(pageSize=100, fields="nextPageToken,mediaItems", pageToken=page_token).execute()
        page_token = results.get('nextPageToken', None)
        items = results.get('mediaItems', [])
        print(f"Got {len(items)} items from google")
        if not items:
            print('No files found.')
        else:
            process_batch(items)
        if not page_token:
            # no more files
            break
        num_errors=0
    except HttpError as e:
        print(e)
        time.sleep(1)
        num_errors = num_errors +1
        if num_errors > max_errors:
            break

print("---------------------")
