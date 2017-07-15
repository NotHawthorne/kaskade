from lxml import html
from subprocess import call
import requests
import sys
import libtorrent as lt
import time
import getpass

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

#Search Result class
class searchResult(object):
    def __init__(self):
        self.torrents = []
        self.links = []
        self.seeds = []
        self.leechers = []

#Download Torrent
def torrentDownload(magnet):
    ses = lt.session()
    params = {'save_path': '/home/'+getpass.getuser()+'/Downloads/'}
    handle = lt.add_magnet_uri(ses, magnet, params)

    print('downloading metadata...')
    while (not handle.has_metadata()): time.sleep(1)
    print('got metadata, starting torrent download...')
    while (handle.status().state != lt.torrent_status.seeding):
        print('%d %% done' % (handle.status().progress*100))
        time.sleep(1)

#Search ThePirateBay
def tpbSearch(searchString):
    #Load page
    page = requests.get('https://thepiratebay.org/search/' + searchString + '/0/99/0')
    tree = html.fromstring(page.content)
    
    result = searchResult()
    result.torrents = tree.xpath('//a[@class="detLink"]/text()')
    result.links = tree.xpath('//a[@title="Download this torrent using magnet"]/@href')

    seedsLeeches = tree.xpath('//td[@align="right"]/text()')
    for x in range(0, len(seedsLeeches)):
        if (x % 2 == 0):
            result.seeds.append(seedsLeeches[x])
        else:
            result.leechers.append(seedsLeeches[x])
    return result;

#Main function
if(len(sys.argv)>=2):
    searchString = sys.argv[1]
    searchResults = []
    outResults = searchResult()
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
        for y in range(0, len(searchResults[x].torrents)):
            outResults.torrents.append(searchResults[x].torrents[y])
            outResults.links.append(searchResults[x].links[y])
            outResults.seeds.append(searchResults[x].seeds[y])
            outResults.leechers.append(searchResults[x].leechers[y])

    for x in range(0, len(outResults.torrents)):
        print('\033[1m'+str(x) + '\033[0m) ' + outResults.torrents[x] + '\033[94m '+outResults.seeds[x]+'\033[0m|\033[91m'+outResults.leechers[x]+'\033[0m')
    torrentSelection = input('Select a torrent(0-'+str(len(outResults.torrents)-1)+'):')
    print('Downloading "'+outResults.torrents[int(torrentSelection)]+'"...')
    torrentDownload(outResults.links[int(torrentSelection)])
    #call('transmission-cli "'+outResults.links[int(torrentSelection)]+'"')
else:
    print('invalid args!')
