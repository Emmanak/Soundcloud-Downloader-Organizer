import itertools
import os
import time
import eyed3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

sys.stdout = open('G:\\Downloads\\scDownloaderOutput.txt', 'w', encoding='utf-8')


#Script Init
filepath = 'G:\\Downloads'
filepath2 = 'G:\\Google Drive\\Hymns'
options = Options()
options.add_argument("user-data-dir=C:\\Selenium\\BrowserProfile")
driver = webdriver.Chrome(options=options,executable_path="G:/My Tools/chromedriver_win32/chromedriver.exe") #G:/My Tools/chromedriver_win32/chromedriver.exe
driver.nameIndex = 0
driver.downloaded = 0
driver.totalSongs = 0




# Start Script - input use profile/tracks
def startScript():
    driver.implicitly_wait(1)
    driver.maximize_window()


#Ending Sequence
def exitScript():
    time.sleep(1)  # Wait to view page
    driver.close()
    driver.quit()
    print("All downloads completed")

#Retrieves User Tracks Webpage
def loadTracks(username):
    driver.get('https://soundcloud.com'+username+'/tracks')

#retrieves User's following webpage
def loadFollowing(username):
    driver.get('https://soundcloud.com'+username+'/following')

#Find single element via xpath
def loadXpath(textString):
    driver.find_element_by_xpath(textString)
#Fine multiple elements via xpath
def loadXpaths(textString):
    driver.find_elements_by_xpath(textString)

#Modify MP3 Tags for Artist, and Album
def mp3Tagger(filepath, name):
 mp3 = eyed3.load(filepath)
 mp3.tag.artist = name
 mp3.tag.album = name
 mp3.tag.save()
 return

def charReplace(filename):
    filename = filename.replace(":", "_")
    filename = filename.replace("~", "_")
    filename = filename.replace("|", "_")
    filename = filename.replace("/", "_")
    filename = filename.replace("\\", "_")
    filename = filename.replace("?", "_")
    filename = filename.replace("/", "_")
    filename = filename.replace("<", "_")
    filename = filename.replace(">", "_")
    filename = filename.replace('"', "_")
    filename = filename.replace('*', "_")
    return filename


#loop through all tracks
def downloadUsers(driver):
    loadTracks('/emmanuel-augustine-3')  # username can be changed to a variable (For Future)
    following = driver.find_element_by_xpath('//td[contains(@class, "infoStats__stat")]/a[contains(@href, "following")]/div').get_attribute("innerText")
    driver.find_element_by_xpath('//td[contains(@class, "infoStats__stat")]/a[contains(@href, "following")]/div').click()
    print("Following: " + str(following))
    followingNum = driver.find_elements_by_xpath('//a[contains(@class, "userBadgeListItem__heading")]')

    while len(followingNum) < int(following)-1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        followingNum = driver.find_elements_by_xpath('//a[contains(@class, "userBadgeListItem__heading")]')
        print('Found '+str(len(followingNum))+' out of '+str(following))
        time.sleep(1)

    time.sleep(6)
    i=0
    usernames = [None]*len(followingNum)
    print(str(len(followingNum))+" users found")
    for name in followingNum:
        usernames[i] = name.get_attribute("pathname")
        i = i+1
    i = 0
    for name in usernames:
        driver.username = name
        i = i + 1
        print("Fetching user " + str(i) + " of " + str(len(usernames)) + ": " + str(driver.username))
        downloadTracks(driver)


def downloadTracks(driver):
    loadTracks(str(driver.username))
    tracks = driver.find_element_by_xpath('//td[@class="infoStats__stat"]/a[contains(@href, "/tracks")]/div').get_attribute("innerText")
    links = driver.find_elements_by_xpath('//a[contains(@class, "soundTitle__title")]/span')
    print("Number of User tracks: "+str(tracks))
    print("Number of tracks found:"+ str(len(links)))




    while len(links) < int(tracks): #Loading all tracks on screen links usually has more tracks than the user actual tracks so the difference needs to be calculated
        links = driver.find_elements_by_xpath('//a[contains(@class, "soundTitle__title")]/span')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
    print("Tracks prepared for download: " + str(tracks))
    time.sleep(5)

    downloads = driver.find_elements_by_xpath('//button[contains(@id, "_")]') #download button locations
    names = driver.find_elements_by_xpath('//a[contains(@class, "soundTitle__username")]/span') #names of users who own the current tracks
    nameIndex = 0
    scroll = 0
    newName = [None] * len(names) #array made to contain new name for renaming downloaded mp3 files
    artistName = [None] * len(names) #array made for checking names are being collected
    downloaded = 0
    previousName = names[nameIndex].get_attribute('innerText')


    for link, download in itertools.zip_longest(links, downloads):
        if nameIndex+1 > int(tracks):
            return

        filename = link.get_attribute('innerText') + '.mp3'
        name = names[nameIndex].get_attribute('innerText')
        driver.execute_script("window.scrollTo(0," + str(scroll) + " )")
        newName[nameIndex] = filename + ' by ' + name
        artistName[nameIndex] = name
        nameIndex = nameIndex + 1
        scroll = scroll + 200

        #A filename cannot contain any of the following characters: \ / : * ? " < > | or in this case ~ as well
        filename = charReplace(filename)
        name = charReplace(name)
        waitTimer = 0
        clicked = 0
        skip = 0
        print("verifying " + filepath + "\\" + filename)

        while not os.path.exists(filepath+"\\"+filename) and not os.path.exists(filepath2 + "\\" + name + "\\" + filename):

            if clicked == 0:
                clicked = 1
                if previousName == artistName[nameIndex-1]:
                    download.click()
                elif previousName != artistName[nameIndex-1]:
                    break

            elif waitTimer > 10:
                skip = 1
                break
            time.sleep(1)
            waitTimer = waitTimer + 1

        print(filepath + "\\" + filename +" downloaded in " + str(waitTimer)+" sec")
        if clicked == 1 and skip == 0:
            mp3Tagger(filepath + "\\" + filename, name)

        if not os.path.exists(filepath2 + "\\" + name) and os.path.exists(filepath + "\\" + filename) and skip == 0:
            try:
                print("Making new folder " + filepath2 + "\\" + name)
                os.makedirs(filepath2 + "\\" + name)
                print("Moving song to " + filepath2 + "\\" + name)
                os.rename(filepath + "\\" + filename, filepath2 + "\\" + name + "\\" + filename)
            except FileExistsError:
                print("The path"+filepath+"\\"+name+" already exists")

        elif os.path.exists(filepath2 + "\\" + name) and os.path.exists(filepath + "\\" + filename) and skip == 0:
            try:
                print("Moving song to " + filepath2 + "\\" + name)
                os.rename(filepath + "\\" + filename, filepath2 + "\\" + name + "\\" + filename)
            except FileExistsError:
                print("You already have "+filename)


        downloaded = downloaded + 1
        print(str(downloaded) + ' out of ' + str(tracks) + ' downloaded in '+ str(waitTimer) + ' sec')




#### SCRIPT FUNCTION CALLS ####
startScript()
downloadUsers(driver)
exitScript()

