# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 10:43:10 2020

@author: Mangalraj
"""

import os 
import pickle
#import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_httplib2  # This gotta be installed for build() to work
import shutil
import requests

def process_batch(mediaItems):
    #list(pageSize=100, fields="nextPageToken,mediaItems(id,filename)").execute()
    for mediaItemResults in mediaItems["mediaItemResults"]:
        mediaItem = mediaItemResults["mediaItem"]
        base_url = mediaItem["baseUrl"]
        metadata = mediaItem["mediaMetadata"]
        filename=mediaItem["filename"]
        #print(f"downloading file: {filename}")
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
                # Open a local file with wb ( write binary ) permission.
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
            print(f'OK {filename} suffix:{url_suffix}')
        else:
            print(f'KO {filename} suffix:{url_suffix}')
        
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
image_list = open("op_2019_20.txt","r")

ids_to_download=[]
for f in image_list:
    kv=f.split(",")
    #print(f"downloading {kv[0]} -> id={kv[1]}")
    ids_to_download.append(kv[1].strip())   
    if(len(ids_to_download) >48):
        print("processing batch: ", ids_to_download)
        mediaItems= service.mediaItems().batchGet(mediaItemIds=ids_to_download).execute()
        process_batch(mediaItems)
        ids_to_download.clear()
image_list.close()
mediaItems= service.mediaItems().batchGet(mediaItemIds=ids_to_download).execute()
process_batch(mediaItems)

#
#
#mediaItems= service.mediaItems().batchGet(mediaItemIds=ids_to_download).execute()
#    base_url = photo_details["baseUrl"]
#    metadata = photo_details["mediaMetadata"]
#    width=photo_metadata ["width"]
#    height=photo_metadata ["height"]
#    filename=photo_details["filename"]
#    
#    base_url_w_size=f"{base_url}=w{width}-h{height}"
#    r = requests.get(base_url_w_size, stream = True)
#    if r.status_code == 200:
#        r.raw.decode_content = True
#            # Open a local file with wb ( write binary ) permission.
#        with open(filename,'wb') as f:
#            shutil.copyfileobj(r.raw, f)
#            
#        print('Image sucessfully Downloaded: ',filename)
#    else:
#        print('Image Couldn\'t be retreived')
#
#
#v_id="AAhbUddfGov6pZa1Nhv4tLVQEY_BRJ6ClP2JkxpoqpYGUx6raoROngv1FSLqvtw6QohZ_Nhk-ZiZJOLujHqv5sxDm8okPmaxag"
#v_details = service.mediaItems().get(mediaItemId=v_id).execute()
#metadata = v_details["mediaMetadata"]
#if "video" in metadata
