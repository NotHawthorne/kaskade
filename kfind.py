from lxml import html
from subprocess import call
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

#Magnet Result class
class magnetResult(object):
    def __init__(self):
        self.name = ''
        self.link = ''
        self.seeds = 0
        self.leechers = 0

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
    #Load page
    page = requests.get('https://thepiratebay.org/search/' + searchString + '/0/99/0')
    tree = html.fromstring(page.content)
    result = []

    torrentResults = tree.xpath('//a[@class="detLink"]/text()')
    torrentLinks = tree.xpath('//a[@title="Download this torrent using magnet"]/@href')
    seedsLeeches = tree.xpath('//td[@align="right"]/text()')

    for x in range(0, len(torrentResults)):
        returnMagnet = magnetResult()
        returnMagnet.name = torrentResults[x]
        returnMagnet.link = torrentLinks[x]
        result.append(returnMagnet)

    curIt = 0
    for x in range(0, len(seedsLeeches)):
        if (x % 2 == 0):
            result[curIt].seeds = seedsLeeches[curIt]
        else:
            result[curIt].leechers = seedsLeeches[curIt]
            curIt += 1
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
            elif(sys.argv[x+2]=="-1337"):
                conf.search1337x = True
            else:
                print('Invalid argument "'+sys.argv[x+2]+'"... ignoring.')
    
    #Search all websites
    if (conf.searchTpb==True):
        searchResults.append(tpbSearch(searchString))

    for x in range(0, len(searchResults)):
        for y in range(0, len(searchResults[x])):
            outResults.append(searchResults[x][y])

    for x in range(0, len(outResults)):
        print(tcBld+str(x)+tcEnd+') ' + outResults[x].name+tcGrn+' '+outResults[x].seeds+tcEnd+'|'+tcRed+outResults[x].leechers+tcEnd)
    torrentSelection = input('Select a torrent(0-'+str(len(outResults)-1)+'):')
    print(tcGrn+'Downloading "'+outResults[int(torrentSelection)].name+'"...'+tcEnd)
    torrentDownload(outResults[int(torrentSelection)].link)
else:
    print('invalid args!')
