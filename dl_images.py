# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 17:16:02 2014

@author: toli
"""

#http://promo.na.leagueoflegends.com/sru-map-assets/6/47/39.png
import urllib.request
import shutil
import io
from PIL import Image

def downloadImages(_h = 47, _v = 40):
    files = {}
    for h in range(0,_h):
        for v in range(0,_v):
            filename = ("./data/new_Sr_{0}_{1}.png".format(h,v))            
            url = "http://promo.na.leagueoflegends.com/sru-map-assets/6/{0}/{1}.png".format(h,v)
            with urllib.request.urlopen(url) as response, open(filename,'wb') as out_file:
                shutil.copyfileobj(response, out_file)
                files[filename] = out_file
        print( h)
    return files

def compositeImage(h, v, size, files):    
    image = Image.new("RGB", (h*size[0],v*size[1]) ,"Black")
    for block in files:
        for index in block:
            sub = Image.open(block[index])
            box = (index[0]*size[0],
                   v*size[1]-(index[1]+1)*size[1],
                   #index[0]*size[0]+size[0],
                   #index[1]*size[1]+size[1]
                   )
            image.paste(sub,box)
            image.save("./data/new_Sr_comp.png")
def determineCompSize(files):
    size = []
    for file in files:
        return Image.open(files[file]).size
    
if __name__ == "__main__":
    _h = 47
    _v = 40
    #downloadImages(_h,_v)
    determineCompSize({'filename':"./data/new_Sr_1_1.png"})
    filePaths = [{(h,v):"./data/new_Sr_{0}_{1}.png".format(h,v)} for h in range(_h) for v in range(_v)]
    compositeImage(_h, _v, size=(256,256), files=filePaths)
    #for h in new_Sr_{0}_{1}
           