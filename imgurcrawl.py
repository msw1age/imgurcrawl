#!/usr/bin/env python3
#Downloads all images from an imgur sub
import os
import sys
import time
import datetime
import shutil
import requests
import bs4

#Time the program
startTime = time.time()

#Exit routine. Prints the time the program ran, the number of files downloaded, and optionally the program's usage.
def printExit(error=True, filesDownloaded = 0):
    if error == True:
        print("Program usage: %s subreddit [optional_mode]\n" % sys.argv[0], 
        "Available modes:\n",
        "\t a to append to a currently existing folder\n",
        "\t w to delete the currently existing folder and make a new one\n",
        "\t n to create a new folder \n",
        "Default behavior is n", sep = "")
    print("Exiting program. Time elapsed: " + str(time.time() - startTime)  
           + " seconds. Files downloaded: " + str(filesDownloaded))
    sys.exit()

#Input: A name for the new folder, and a mode to use if we run into an existing folder.
#Returns the name of the folder we will use.
def createFolder(folderName, mode='n'):
    folderExists = False
    for folder in os.listdir('.'):
        if sys.argv[1] in folder:
            folderExists = True
            if mode == 'a':
                print("Adding to folder " + folder)
                return folder
            elif mode == 'w':
                print("Deleting folder " + folder + " and creating folder " + folderName)
                shutil.rmtree(folder)
                os.makedirs(folderName)
                return folderName
            elif mode == 'n':
                print("Creating folder " + folderName)
                os.makedirs(folderName)
                return folderName
            else:
                printExit()
    if folderExists == False:
        print("Creating folder " + folderName)
        os.makedirs(folderName)
        return folderName

#Download all images from the given sub 
def downloadFiles(folderName, sub):
    filesDownloaded = 0
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        print("Downloading all images from /r/" + sub)
        mainPageRequest = requests.get("http://imgur.com/r/" + sub, headers=headers)
        mainPageRequest.raise_for_status()
        mainPage = bs4.BeautifulSoup(mainPageRequest.text, features="lxml")
        #All images on an imgur page are in an <a> element with an image-list-link class
        for link in mainPage.find_all("a", {"class": "image-list-link"}):
            try:
                #The title of a picture is in a <p> element in a <div> element right after the <a> element.
                #Replacing / with _ prevents an error with file creation on Linux and OS X.
                pictureName = link.findNextSibling().find('p').getText().replace("/", "_")
                #The link to the picture with the sub info removed and a '.jpg' appended is the actual file.
                imageLink = "http://i.imgur.com/" + link["href"].replace("/r/" + sys.argv[1], "") + ".jpg"
                imageRequest = requests.get(imageLink, headers=headers)
                imageRequest.raise_for_status()
                #Create a new file inside our folder and increment the number of files we've downloaded by 1
                with open(folderName + os.sep + pictureName + ".jpg", 'wb') as pictureFile:
                    for chunk in imageRequest.iter_content(8192):
                        pictureFile.write(chunk)
                    print("Downloaded file " + pictureName + ".jpg")
                    filesDownloaded += 1
            except OSError as err:
                print("OSError: " + str(err))
    except KeyboardInterrupt: 
        pass
    printExit(error=False, filesDownloaded=filesDownloaded)

#Create the folder and download files based on the command line args
if len(sys.argv) in [2, 3]:
    sub = sys.argv[1]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    folderName = sub + " " + now
    if len(sys.argv) == 3:
        folderName = createFolder(folderName, sys.argv[2])
    else:
        folderName = createFolder(folderName)
    downloadFiles(folderName, sub)
else:
    printExit()
