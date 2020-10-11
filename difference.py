# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 20:12:55 2020

@author: Mangalraj
"""
def Diff(list1, list2): 
    return list(set(list1)-set(list2))
#(list(list(set(list1)-set(list2)) + list(set(list2)-set(list1)))) 

file_list=[]
file = open("file_2019_20","r")
for f in file:
    file_list.append(f.strip())
file.close()

google_list={}
google = open("google_2019_20","r")
for f in google:
    kv=f.split(",")
    google_list[kv[0] ] = kv[1]
google.close()

diff = Diff(google_list.keys(),file_list)

missing_entries = { your_key: google_list[your_key] for your_key in diff }


op = open("op_2019_20.txt","w")
for key,value in missing_entries.items():
    op.write("{0},{1}".format(key,value))
    #op.write("\n")
op.close()
