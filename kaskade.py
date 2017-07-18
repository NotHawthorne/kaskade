from lxml import html
from subprocess import call
import operator
import requests
import sys
import libtorrent as lt
import time
import getpass

#Terminal output colors
tcRed = '\033[91m'
tcGrn = '\033[94m'
tcBld = '\033[1m'
tcEnd = '\033[0m'
tcPnk = '\033[35m'
tcBlu = '\033[34m'
tcYlw = '\033[33m'

#Config class
class searchConfig(object):
    def __init__(self):
        self.searchTpb = False
        self.search1337x = False
        self.searchKatcr = False
        self.searchLimetorrents = False
        self.searchRARBG = False
        self.searchRutracker = False
        self.searchSkytorrents = False
        self.searchToorgle = False
        self.searchTorrentz2 = False
        self.searchTorrentproject = False
        self.searchZooqle = False
        self.searchNyaa = False
        self.searchDemonoid = False
        self.maxResults = 100

#Magnet Result class
class magnetResult(object):
    def __init__(self):
        self.name = ''
        self.link = ''
        self.seeds = 0
        self.leechers = 0

#Strip array of 0-seeder entries
def removeNullSeeds(resultArray):
    outArray = []
    existingMagnets = []
    stripArray = []

    for x in range(0, len(resultArray)):
        if (int(resultArray[x].seeds) > 0):
            if (resultArray[x].link.strip() in existingMagnets):
                pass
            else:
                outArray.append(resultArray[x])
                existingMagnets.append(resultArray[x].link.strip())

    sortArray = sorted(outArray, key=operator.attrgetter('seeds'))
    return list(reversed(sortArray))

#Download Torrent
def torrentDownload(magnet):
    ses = lt.session()
    params = {'save_path': '/home/'+getpass.getuser()+'/Downloads/'}
    handle = lt.add_magnet_uri(ses, magnet, params)

    print('downloading metadata...')
    while (not handle.has_metadata()): time.sleep(1)
    print('got metadata, starting torrent download...')
    while (handle.status().state != lt.torrent_status.seeding):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print('%d %% done' % (handle.status().progress*100))
        time.sleep(1)

#Search ThePirateBay
def tpbSearch(searchString):
    print(tcYlw+'Searching thepiratebay.se...'+tcEnd)
    #Load page
    page = requests.get('https://thepiratebay.org/search/' + searchString + '/0/99/0')
    tree = html.fromstring(page.content.decode('utf-8', 'ignore'))
    result = []

    torrentResults = tree.xpath('//a[@class="detLink"]/@title')
    torrentLinks = tree.xpath('//a[@title="Download this torrent using magnet"]/@href')
    seedsLeeches = tree.xpath('//td[@align="right"]/text()')

    for x in range(0, len(torrentResults)):
        returnMagnet = magnetResult()
        returnMagnet.name = (tcYlw+'[TPB]'+tcEnd)+torrentResults[x].replace('Details for ','')
        returnMagnet.link = torrentLinks[x]
        result.append(returnMagnet)
    curIt = 0
    for x in range(0, len(seedsLeeches)):
        if (x % 2 == 0):
            result[curIt].seeds = int(seedsLeeches[x])
        else:
            result[curIt].leechers = int(seedsLeeches[x])
            curIt += 1
    return result;

#Search Demonoid
def demonoidSearch(searchString):
    print(tcBlu+'Searching demonoid.pw...'+tcEnd)
    #Load page
    page = requests.get('https://www.demonoid.pw/files/?category=0&subcategory=All&quality=All&seeded=2&external=2&query='+searchString+'&uid=0&sort=S')
    tree = html.fromstring(page.content.decode('utf-8', 'ignore'))
    result = []

    torrentResults = tree.xpath('//td[@class="tone_1_pad"]/a/text()')
    torrentResults2 = tree.xpath('//td[@class="tone_3_pad"]/a/text()')
    torrentLinks = tree.xpath('//a[img[@title="Download as magnet"]]/@href')
    seeds = tree.xpath('//font[@class="green"]/text()')
    leeches = tree.xpath('//font[@class="red"]/text()')
    mergedTorrentResults = []
    for x in range(0, len(torrentResults)):
            mergedTorrentResults.append(torrentResults[x])
            mergedTorrentResults.append(torrentResults2[x])
    
    for x in range(0, len(mergedTorrentResults)):
        returnMagnet = magnetResult()
        returnMagnet.name = (tcBlu+'[DEM]'+tcEnd)+mergedTorrentResults[x].strip()
        returnMagnet.link = torrentLinks[x].strip()
        returnMagnet.seeds = int(seeds[x])
        returnMagnet.leechers = int(leeches[x])
        result.append(returnMagnet)

    return result;

#Search NyaaPantsu
def nyaaSearch(searchString):
    print(tcPnk+'Searching nyaa.pantsu.cat...'+tcEnd)
    #Load page
    page = requests.get('https://nyaa.pantsu.cat/search?c=_&s=0&limit=50&order=false&q='+searchString+'&s=0&sort=5&userID=0')
    tree = html.fromstring(page.content.decode('utf-8', 'ignore'))
    result = []

    torrentResults = tree.xpath('//td[@class="tr-name home-td"]/a/text()')
    torrentLinks = tree.xpath('//a[@title="Magnet Link"]/@href')
    seeds = tree.xpath('//td[@class="tr-se home-td hide-xs"]/text()')
    leeches = tree.xpath('//td[@class="tr-le home-td hide-xs"]/text()')
    
    for x in range(0, len(torrentResults)):
        returnMagnet = magnetResult()
        returnMagnet.name = (tcPnk+'[NYA]'+tcEnd)+torrentResults[x].strip()
        returnMagnet.link = torrentLinks[x].strip()
        returnMagnet.seeds = int(seeds[x])
        returnMagnet.leechers = int(leeches[x])
        result.append(returnMagnet)

    return result;

#Main function
if(len(sys.argv)>=2):
    searchString = sys.argv[1]
    searchResults = []
    outResults = []
    sitesToSearch = []
    conf = searchConfig()

    if (len(sys.argv)>2):
        for x in range(0, len(sys.argv)-2):
            if(sys.argv[x+2]=="-tpb"):
                conf.searchTpb = True
            elif(sys.argv[x+2]=="-nyaa"):
                conf.searchNyaa = True
            elif(sys.argv[x+2]=="-dem"):
                conf.searchDemonoid = True
            elif("-max" in sys.argv[x+2]):
                conf.maxResults = int(sys.argv[x+2].replace("-max=", ""))
            else:
                print('Invalid argument "'+sys.argv[x+2]+'"... ignoring.')
    
    #Search all websites
    if (conf.searchTpb==True):
        searchResults.append(tpbSearch(searchString))
    if (conf.searchNyaa==True):
        searchResults.append(nyaaSearch(searchString))
    if (conf.searchDemonoid==True):
        searchResults.append(demonoidSearch(searchString))

    for x in range(0, len(searchResults)):
        for y in range(0, len(searchResults[x])):
            outResults.append(searchResults[x][y])

    outResults = removeNullSeeds(outResults)
    if (len(outResults)>conf.maxResults):
        outResults = outResults[:conf.maxResults]

    for x in range(0, len(outResults)):
        outputString = tcBld+str(x)+tcEnd+') '+outResults[x].name+tcGrn+' '+str(outResults[x].seeds)+tcEnd+'|'+tcRed+str(outResults[x].leechers)+tcEnd
        outputString.replace("\n", "")
        print(outputString)
    torrentSelection = input('Select a torrent(0-'+str(len(outResults)-1)+'):')
    print(tcGrn+'Downloading "'+outResults[int(torrentSelection)].name+'"...'+tcEnd)
    torrentDownload(outResults[int(torrentSelection)].link)
else:
    print('invalid args!')
