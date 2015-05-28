import urllib2
import urllib
import json
import subprocess
import os
from pymongo import MongoClient



def downloadImagefiles():
    os.chdir('./medium_images')
    collection = getCollection()
    for photo in collection.find():
        downloadFile(photo[u'photo_file_url'], 'mediumImages')

def getCollection():
    client = MongoClient()
    db = client['urbanPhotoDatabase']
    collection = db['wroclaw']
    return collection

def insertPictureInfosToDB():
    PANORAMIO_REQUEST_LIMIT = 499
    useProxy()
    photoList = getWroclawImageList(PANORAMIO_REQUEST_LIMIT)

    collection = getCollection()
    collection.insert(photoList)
    

def getWroclawImageList(REQUEST_LIMIT):
    imageSetBegin = 0
    imageSetEnd = REQUEST_LIMIT

    photoList = []
    hasMore = True
    while hasMore:
        data = json.loads(getWroclawImageInformation(imageSetBegin, imageSetEnd))

        photoList.extend(data['photos'])
        imageSetBegin += REQUEST_LIMIT
        imageSetEnd += REQUEST_LIMIT
        hasMore = u'True' == str(data['has_more'])
    
    return photoList

def getHTTPHeaders():
    return {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'}

def getImageInformation(urlParams):
    url = "http://www.panoramio.com/map/get_panoramas?" + urllib.urlencode(urlParams)
    req = urllib2.Request(url, None, getHTTPHeaders())
    return urllib2.urlopen(req).read()

def getWroclawImageInformation(imageSetBegin, imageSetEnd):
    Wroclaw_miny = 51.042244
    Wroclaw_maxy = 51.209747
    Wroclaw_minx = 16.807158
    Wroclaw_maxx = 17.176217
    
    urlParams = {"order":"upload_date",
                 "set":"public",
                 "size":"medium",
                 "from":imageSetBegin,
                 "to":imageSetEnd,
                 "minx":Wroclaw_minx,
                 "miny":Wroclaw_miny,
                 "maxx":Wroclaw_maxx,
                 "maxy":Wroclaw_maxy
                 }
    
    
    return getImageInformation(urlParams)

def downloadFile(url, path = ''):
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    print os.path.join(path, file_name)
    f = open(os.path.join(path, file_name), 'wb')
    meta = u.info()
    file_size = 0
    try:
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
    except:
        print "unable to determine file size"
    file_size_dl = 0
    block_sz = 8192
    while True:
        fileBuffer = u.read(block_sz)
        if not fileBuffer:
            break
    
        file_size_dl += len(fileBuffer)
        f.write(fileBuffer)
        if(file_size):
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,
    
    f.close()
    

if __name__ == "__main__":
    downloadImagefiles()
    pass