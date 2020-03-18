import itertools
import os
import time
import eyed3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


#Script Init
filepath = 'G:\\Downloads'
options = Options()
options.add_argument("user-data-dir=C:\\Selenium\\BrowserProfile")
driver = webdriver.Chrome(options=options,executable_path="G:/Downloads/chromedriver_win32/chromedriver.exe")
driver.nameIndex = 0
driver.downloaded = 0
driver.totalSongs = 0




# Start Script - input use profile/tracks
def startScript():
    driver.implicitly_wait(1)
    driver.maximize_window()
    #driver.get('chrome://extensions/')
    #for i in range(5):
        #print(i)
        #time.sleep(1)


#Ending Sequence
def exitScript():
    time.sleep(1)  # Wait to view page
    driver.close()
    driver.quit()
    print("Test completed")

def loadTracks(username):
    driver.get('https://soundcloud.com'+username+'/tracks')

def loadFollowing(username):
    driver.get('https://soundcloud.com'+username+'/following')

def loadXpath(textString):
    driver.find_element_by_xpath(textString)

def loadXpaths(textString):
    driver.find_elements_by_xpath(textString)

def mp3Tagger(filepath, name):
 mp3 = eyed3.load(filepath)
 #newName = 'u"{}"'.format(name)
 mp3.tag.artist = name
 mp3.tag.album = name
 mp3.tag.save()
 return

startScript()


#loop through all tracks
def downloadUsers(driver):
    loadTracks('/emmanuel-augustine-3')  # username can be chanegd to a variable
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
        #downloadTracks(driver)
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



    #print("Following: "+str(following))

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
        #print('downloading:...' + newName[nameIndex])
        nameIndex = nameIndex + 1
        scroll = scroll + 200


        #if (nameIndex > 1) and (nameIndex < len(names) + 1) and (artistName[nameIndex - 1] != previousName):
            # print(artistName[nameIndex - 2])
            # print(previousName)
            #print('************************* DOWNLOAD FAILED ****************************')
            #continue


        filename = filename.replace(":", "_")
        filename = filename.replace("~", "_")
        filename = filename.replace("|", "_")
        waitTimer = 0
        clicked = 0
        while not os.path.exists(filepath+"\\"+filename):
            print("verifying "+filepath+"\\"+filename)
            #time.sleep(1)
            waitTimer = waitTimer + 1


            if clicked == 0 and not (os.path.exists(filepath + "\\" + name + "\\" + filename)) and not (os.path.exists(filepath+"\\"+filename)):
                print('downloading:...' + filename+' by '+name)
                download.click()
                clicked = 1
                #time.sleep(4)
            elif os.path.exists(filepath+"\\"+filename):
                mp3Tagger(filepath+"\\"+filename, name)



                if not os.path.exists(filepath+"\\"+name):
                    try:
                        print("Making new folder "+filepath+"\\"+name)
                        os.makedirs(filepath+"\\"+name)

                        #os.rename(filepath + "\\" + filename, filepath + "\\" + name + "\\" + filename)
                    except FileExistsError:
                        # directory already exists
                        break
                elif os.path.exists(filepath + "\\" + name):
                    try:
                        print("Moving song to " + filepath + "\\" + name)
                        os.rename(filepath + "\\" + filename, filepath + "\\" + name + "\\" + filename)
                    except FileExistsError:
                        # directory already exists
                        break

                try:
                    print("Moving song to " + filepath + "\\" + name)
                    os.rename(filepath + "\\" + filename, filepath + "\\" + name + "\\" + filename)
                except FileExistsError:
                    # directory already exists
                    break

            elif os.path.exists(filepath+"\\"+filename) and os.path.exists(filepath + "\\" + name):
                print("Moving song to " + filepath + "\\" + name)
                os.rename(filepath + "\\" + filename, filepath + "\\" + name + "\\" + filename)
                break
            elif os.path.exists(filepath + "\\" + name + "\\" + filename):
                print("You already have this song")
                break
            #elif waitTimer > 5:
                #print("Moving to next track")
                #break
        #time.sleep(5)
        #if os.path.exists(filepath+"\\"+filename) and os.path.exists(filepath + "\\" + name):
            #try:
               # print("Moving song to " + filepath + "\\" + name)
               # os.rename(filepath + "\\" + filename, filepath + "\\" + name + "\\" + filename)
            #except FileExistsError:
                #print("ERROR: File already exists. Move cancelled")
                #break
        downloaded = downloaded + 1
        print(str(downloaded) + ' out of ' + str(tracks) + ' downloaded in '+ str(waitTimer) + ' sec')

        # newfilename = link.get_attribute('innerText') + 'by Emmanuel Augustine' + '.mp3'
        # filename = max([filepath + "\\" + f for f in os.listdir(filepath)], key=os.path.getctime)
        # shutil.move(os.path.join(filepath, ), newfilename)





startScript()
downloadUsers(driver)
#driver.username = '/notesofgladness'
#downloadTracks(driver)

#links = driver.find_elements_by_xpath('//a[contains(@class, "soundTitle__title")]/span')
#while driver.nameIndex < len(links):
 #   print(links[driver.nameIndex].get_attribute('innerText')+'mp3')
  #  driver.nameIndex = driver.nameIndex + 1


#print(str(driver.downloaded)+' out of '+str(driver.totalSongs)+' downloaded')
#print(driver.nameIndex)


exitScript()

