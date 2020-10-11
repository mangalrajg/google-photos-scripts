# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 20:02:48 2020

@author: Mangalraj
"""
import os

root = "C:\\Users\\Mangalraj\\Pictures"
#path = os.path.join(root, "targetdirectory")
op=open("file_image_list.txt","w",encoding='utf-8')

for r,d,f in os.walk(root):
    for file in f:
        op.write(file)
        op.write("\n")
op.close()