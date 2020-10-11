# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 20:12:55 2020

@author: Mangalraj
"""
def Diff(list1, list2): 
    return list(set(list1)-set(list2))

file_image_list="file_image_list.txt"
google_image_list="google_image_list.txt"
output_image_list="op_image_list.txt"

file_list=[]
file = open(file_image_list,"r")
for f in file:
    file_list.append(f.strip())
file.close()

google_list={}
google = open(google_image_list,"r")
for f in google:
    kv=f.split(",")
    google_list[kv[0] ] = kv[1]
google.close()

diff = Diff(google_list.keys(),file_list)
missing_entries = { your_key: google_list[your_key] for your_key in diff }


op = open(output_image_list, "w")
for key,value in missing_entries.items():
    op.write("{0},{1}".format(key,value))
op.close()
