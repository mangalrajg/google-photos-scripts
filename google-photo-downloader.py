# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 10:43:10 2020

@author: Mangalraj
"""

import os 
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_httplib2  # This gotta be installed for build() to work
import shutil
import requests

def process_batch(mediaItems):
    for mediaItemResults in mediaItems["mediaItemResults"]:
        mediaItem = mediaItemResults["mediaItem"]
        base_url = mediaItem["baseUrl"]
        metadata = mediaItem["mediaMetadata"]
        filename=mediaItem["filename"]
        url_suffix=""
        if "video" in metadata:
            url_suffix="dv"
        else:
            width=metadata ["width"]
            height=metadata ["height"]
            url_suffix=f"w{width}-h{height}"
    
        base_url_w_suffix=f"{base_url}={url_suffix}"
        r = requests.get(base_url_w_suffix, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
            print(f'OK {filename} suffix:{url_suffix}')
        else:
            print(f'KO {filename} suffix:{url_suffix}')
        
# Setup the Photo v1 API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
# List of image filemane + id's in csv format 
image_id_list="op_2019_20.txt"

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
image_list = open(image_id_list,"r")

ids_to_download=[]
for f in image_list:
    kv=f.split(",")
    ids_to_download.append(kv[1].strip())   
    if(len(ids_to_download) >48):
        print("processing batch: ", ids_to_download)
        mediaItems= service.mediaItems().batchGet(mediaItemIds=ids_to_download).execute()
        process_batch(mediaItems)
        ids_to_download.clear()
image_list.close()
mediaItems= service.mediaItems().batchGet(mediaItemIds=ids_to_download).execute()
process_batch(mediaItems)

print("----------------------------------")
