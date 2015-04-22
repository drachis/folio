# flash game size analysis
from difflib import SequenceMatcher
import csv
import os.path as path

if __name__ == '__main__':
    #place the script file next to the source file and change the name here.
    sourceFilePath = '../data/CS_Bonus Report.txt'
    buildLogToCSV(sourceFilePath)
    # to quickly convert more than one log at once
    multiSourceFilePaths = [
            '../data/CS_Bonus Report.txt',
            '../data/CS_Bonus Report.txt',
            '../data/CS_Bonus Report.txt'
            ]
    # un comment (remove #) from the next line to run on multipule files
    multiLogToCSV(multiSourceFilePaths)  
    
def multiLogToCSV(sourceFilePaths):
    for sourcePath in sourceFilePaths:
        buildLogToCSV(sourcePath)        
        
def buildLogToCSV(sourceFilePath):
    f = open(sourceFilePath)
    headerIdxs = []
    lines = []
    # read in the lines and find the header blocks.
    for idx,l in enumerate(f):
        if  "-------" in l:
            headerIdxs.append(idx-1)
        lines.append(l)
    f.close()
    # the dash delimiters are only as long as their information
    # we can use this to break lines by data type,
    # we are only interested in the last section at the moment (images)
    # -1 to get last index, +1 to get back to the dashed lined
    dashes = lines[(headerIdxs[-1]+1)][:-2].split("    ",4)
    dashLength = [len(x) for x in dashes]
    
    # image information takes up the last block of the file, here we isolate that
    images = lines[(headerIdxs[-1]+2):len(lines)]
    imageInfo = []
    sizeCompressed = {}
    sizeUncompressed = {}
    s = SequenceMatcher()
    #extact the data from the source file and organize it into an array
    # data format is [[filename, compressed size, uncompressed size, compression format]]
    for idx in range(0,len(images)):
        if images[idx] != "\n":
            imageInfo.append([
                images[idx][:dashLength[0]].strip(),
                int(images[idx][dashLength[0]+4:dashLength[0]+4+dashLength[1]]),
                int(images[idx][dashLength[0]+4+dashLength[1]+4:dashLength[0]+4+dashLength[1]+4+dashLength[2]]),
                images[idx][dashLength[0]+4+dashLength[1]+4+dashLength[2]+4:-2]
                ])
    imageInfo = sorted(imageInfo)
    numImages = len(imageInfo)
    idx = 0
    while idx < numImages:
        # split data into, name, size compressed, size uncompressed, format
        # compression type can extend past dashes.
        if idx+1 < numImages:
            #compare sequential names of images
            imgIndex = imageInfo[idx][0]
            sizeCompressed[imgIndex] = imageInfo[idx][1]
            sizeUncompressed[imgIndex] = imageInfo[idx][2]
            s.set_seqs(imgIndex,imageInfo[idx+1][0])            
            # add all sizes until name match is too low
            idx+=1
            while s.ratio() > 0.6:                
                # step to next image and increase idx, may require everything to be in while loops all the way down.
                if len(imgIndex) != len(imageInfo[idx][0]):
                    #image sequences have the same string length\
                    #print imageInfo[idx][0]
                    break
                #print imgIndex, imageInfo[idx][0] , s.ratio()
                sizeCompressed[imgIndex] += imageInfo[idx][1]
                sizeUncompressed[imgIndex] += imageInfo[idx][2]
                idx+=1
                if idx < numImages:
                    s.set_seqs(imgIndex,imageInfo[idx][0])                
                else:
                    break
    # write out the csv file 
    outputFilePath = path.splitext(path.split(sourceFilePath)[1])[0]
    with open('flash_size_{}.csv'.format(outputFilePath),'w') as csvfile:
       csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
       for elem in sorted(sizeCompressed):
           csvwriter.writerow([elem,"{}".format(sizeCompressed[elem]),"{}".format(sizeUncompressed[elem])])
    print "Extracting sizes from {} complete".format(sourceFilePath)    
    
                
            
    
