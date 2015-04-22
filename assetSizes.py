# -*- coding: utf-8 -*-
"""
Analyze the Unity build log 
to help determine what are the best targets for 
game size reduction 
"""
import os
import pylab as P

def splitFile(fLines,startLine = 31):
    """
    Specialized for the project to pull log file data apart
    """
    gLines = []
    for idx, line in enumerate(fLines[startLine:]):
        if "exec" in line:
            splitLine = line.split(None,5)        
            gLines.append(splitLine)
    return gLines

def processData(data):
    """
    splits incomming data into dictionary assets
    mapping their attributes  to keys.
    """
    assets = {}
    for asset in data:
        path, name = os.path.split(asset[5])
        fileType = None
        if "." in name:
            fileType = name.split(".")[1].strip()
        size = expandNotation(asset[2],asset[3])
        percent = asset[4]
        path = asset[5]
        if fileType != None:
            assets[path] = {'name':name,
                        'size':size,
                        'extension':fileType,
                        'percent':percent,
                        'path':path}
    return assets

def sortByKey(assets, key):
    """
    returns a dictionary of lists 
    in the format;
     {key value:[list of assets containing key value]}
    """
    byExt = {}
    for _key in assets:
        asset = assets[_key]
        if asset[key] != None:
            if asset[key] not in byExt:
                byExt[asset[key]] = [asset]
            if asset[key] in byExt:
                byExt[asset[key]].append(asset)
    return byExt

def sizeByKey(byType):
    """
    prints values by key size
    returns a list of asset type : sizes
    """
    sizes = {}
    for _type in byType:
        sizes[_type] = []
        sizeSum = 0
        for elem in byType[_type]:
            sizeSum += elem['size']
            sizes[_type].append(elem['size'])
        print(_type, "{:,}".format(sizeSum))
    print("\n")
    return sizes

def filterOutValue(assets, value):
    """
    removes all assets who have value in the string of their key
    """
    filtered = {}
    for _key in assets:
        key = _key
        if value not in key:
            filtered[key] = assets[key]
    return filtered
    
def expandNotation(size, notation):
    """
    convert from 99 MB or 99 KB to number of bytes 
    """
    notations = {'mb':2**20, 'kb':2**10 }
    if notation in notations:
        return int(float(size)*notations[notation])
    return size
    
def compactNotation(size, notation):
    """
    convert byte values to MB and KB
    """
    notations = {'mb':2**20, 'kb':2**10 }    
    if notation in notations:
        notation = "{0:.3} {1}".format(float(size)/notations[notation], notation)
    return notation

def graphSize(sizes,name):
    """
    Graph rendering
    """
    n,bins,patches = P.hist(sizes,10, normed=0, histtype='bar')
    P.setp(patches, 'facecolor', 'b', 'alpha', 0.75)
    P.figure()
    P.title(name)
    P.show() 

if __name__ == "__main__":
    f = open("data/buildLog.txt",'r')
    fLines = f.readlines()
    f.close()
    data = splitFile(fLines,1)
    processed = processData(data)
    sizes_p = sizeByKey(sortByKey(processed,"extension"))    
    noExternal = filterOutValue(processed, "ExternalTextures")
    sizes = sizeByKey(sortByKey(noExternal,"extension"))    
    for ext in sizes_p:
        graphSize(sizes[ext],ext)