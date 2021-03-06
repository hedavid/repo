#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json,io
import time
import base64
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
delf=0

xbmcplugin.setContent(addon_handle, 'movies')

baseurl="https://www.filmfriend.de"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)


icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
cookiestring=""


if not xbmcvfs.exists(temp):  
    xbmcvfs.mkdirs(temp)
if not xbmcvfs.exists(temp+"/Filme"):  
    xbmcvfs.mkdirs(temp+"/Filme")
cookie=os.path.join( temp, 'cookie.jar')
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)                  

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def addDir(name, url, mode, thump, desc="",page=1,serie=0,genre=0):   
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&serie="+str(serie)+"&genre="+str(genre)
  ok = True
  liz = xbmcgui.ListItem(name)  
  liz.setArt({ 'fanart' : thump })
  liz.setArt({ 'thumb' : thump })
  liz.setArt({ 'banner' : icon })
  liz.setArt({ 'fanart' : icon })
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, thump, fanart='',duration="", desc="", genre='',director="",year="",bewertung="",mpd="",key="",cast=[],poster=''):
  debug("URL ADDLINK :"+url)
  debug( icon  )
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&mpd="+str(mpd)+"&key="+str(key)
  ok = True
  if fanart=='':
      fanart=icon
  liz = xbmcgui.ListItem(name,thumbnailImage=thump)
  liz.setArt({ 'fanart' : fanart,'poster':poster})
  liz.setInfo(type="Video", infoLabels={"Title": name.strip(), "Plot": desc.strip(), "genre": genre, "Director":director,"Rating":bewertung,"year":year,"Cast":cast})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
	#xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


def geturl(url,data="x",header="",referer=""):
        global cookiestring
        global cj
        debug("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        if not referer=="":
           opener.addheaders = [('Referer', referer)]

        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #debug( e.code )  
             cc=e.read()  
             debug("Error : " +cc)
             content=""
       
        opener.close()
        cookiestring=""
        debug(cookie)
        for cookiex in cj:           
           cookiestring=cookiestring+cookiex.name+"="+cookiex.value+"; "        
        return content


    

   
def login_berlin():
  debug("login_berlin")
  username=addon.getSetting("username")
  password=addon.getSetting("password")
  page="https://www.filmfriend.de/customers/oauth/login/"
  content=geturl(page)
  newlink=re.compile('window.location="(.+?)"\' id="login-berlin"', re.DOTALL).findall(content)[0]       
  contentnew=geturl(newlink)
  page="https://www.voebb.de/oidcp/logincheck"       
  values = { 'L#AUSW' : username,
              'LLOGIN' : "Anmelden",
              'LPASSW' : password,       
            }
  data = urllib.urlencode(values)
  headers = {'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
   'Origin':              'https://www.voebb.de',
   'Upgrade-Insecure-Requests':                      "1",
   'Referer':                  'https://www.voebb.de/oidcp/logincheck',
   "Content-Type": "application/x-www-form-urlencoded",
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",

   }

  content=geturl(page,data=data)
  if "Your password is incorrect" in content:
    dialog = xbmcgui.Dialog()
    dialog.notification("Error", "Username Password ist falsch", xbmcgui.NOTIFICATION_ERROR)
    xbmcvfs.delete(cookie)
    return        
  else:
    debug(content)
    urlz="https://www.voebb.de/oidcp/consent"
    values = {
        'CLOGIN': "Zustimmen und fortfahren"
    }
    data = urllib.urlencode(values)  
    content = requests.post(urlz,data=data, allow_redirects=False,verify=False,cookies=cj,headers=headers)  
    debug(content.text)
    lasturl=content.headers['Location']
    content=geturl(lasturl)  

def getfilm(url):
  debug("GETFILM :"+url)
  global delf
  content=geturl(url)
  debug("?????????????")
  debug(  content)
  debug("?????????????")
  global cookie
  if "Bitte melden Sie sich erst mit" in  content:
    dialog = xbmcgui.Dialog()
    dialog.notification("Error", "Username Password ist falsch", xbmcgui.NOTIFICATION_ERROR)
    delf=1
    xbmcvfs.delete(cookie)
    return          
  debug("#######")
  debug(cookiestring)
  debug("#######")
  newlink=re.compile('data-manifest-url="([^"]+)" data-drm-session-key="([^"]+)"', re.DOTALL).findall(content) 
  mpd=newlink[0][0]
  key=newlink[0][1]
  listitem=widevinelist(mpd,key,url)
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
def widevinelist(mpd,key,url):
  global cookiestring
  debug("???????????")
  licurl=geturl("https://www.filmfriend.de/expressplay/license/license/?type=widevine",data="key="+key)
  licurl=licurl.strip()  
  debug("MPD :"+mpd)
  debug("KEY :"+key)
  debug("CONTENT :")
  debug("--------------------------------------")
  co=urllib.quote_plus(cookiestring)
  header="Cookie="+co+"&User-Agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F65.0.3325.181%20Safari%2F537.36&X-Requested-With=XMLHttpRequest&Accept=text%2Fplain%2C%20%2A%2F%2A%3B%20q%3D0.01&Origin=https%3A%2F%2Fwww.filmfriend.de&Connection=keep-alive&Referer=https%3A%2F%2Fwww.filmfriend.de%2Ffindet-dorie-online-stream.html&Content-Type=application%2Fx-www-form-urlencoded%3B%20charset%3DUTF-8"
  listitem = xbmcgui.ListItem(path=mpd)
  listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')  
  listitem.setProperty('inputstream.adaptive.license_key', licurl+"|content-type=application/octet-stream'&User-Agent=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F65.0.3325.181%20Safari%2F537.36&Referer="+url+"&Origin=https://www.filmfriend.de|R{SSM}|")  
  listitem.setProperty('inputstreamaddon', "inputstream.adaptive")  
  listitem.setProperty("inputstream.adaptive.manifest_type", "mpd")  
  return  listitem
  
def getserie(url):
  global cookiestring
  global cookie
  global delf
  debug(cookiestring)
  debug("########-----#####")  
  headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
   'Connection':'keep-alive',
   'Cache-Control':'max-age=0',
   'Upgrade-Insecure-Requests':'1',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
   'Accept-Encoding': 'gzip, deflate, br'
   }
  debug("GETSERIE :"+url)
  content = requests.get(url, allow_redirects=False,verify=False,cookies=cj,headers=headers)  
  content =content.text.encode("utf-8")
  debug(content)
  if "Bitte melden Sie sich erst mit" in  content:
    dialog = xbmcgui.Dialog()
    dialog.notification("Error", "Username Password ist falsch", xbmcgui.NOTIFICATION_ERROR)
    debug(cookie)
    xbmcvfs.delete(cookie)         
    delf=1
    return    
  else:    
    #content=geturl(url) 
    debug("-------->")    
    debug(content)
    debug("-------->")
    jsonf=re.compile("JSON.parse\('(.+?)'\);", re.DOTALL).findall(content)[0]      
    debug("JSON")
    debug(jsonf)
    struktur = json.loads(jsonf)
    for element in   struktur:
        debug("####")
        debug(element)
        addLink(element["name"],url,"playdash","",mpd=element["manifestUrl"],key=element["drmSessionKey"])
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def playdash(mpd,key,url):    
    debug("playdash")
    debug(mpd)
    debug(key)
    listitem=widevinelist(mpd,key,"")
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
def login():
     
    type=addon.getSetting("btype")
    debug("TYPE :")
    debug(type)
    if type=="Berlin":
       login_berlin()
       
def playit(url):      
    
    getfilm(url)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
    
def rubrik(url,page=1,serie=0,genre=0):
    debug("Rubrik")
    debug(serie) 
    genre=int(genre)
    
    weiter=True
    while weiter:
        if genre==0:
            starturl=url+"&p="+str(page)
        else:
            starturl=url
            weiter=False
        content=geturl(starturl) 
        htmlPage = BeautifulSoup(content, 'html.parser')
        elemente = htmlPage.find_all("li",attrs={"class":re.compile("col-sm-6 col-md-4 col-lg-3 col-xlg-2 item last catPad mbottom-30")})
        for element in elemente: 
           link=element.find("a")["href"]
           title=element.find("div",attrs={"class":"title product-name"})
           if element.find("img",attrs={"class":"resp","class":"pabs"}):
               imgtag=element.find("img",attrs={"class":"resp","class":"pabs"})
           else:
               imgtag=element.find("img",attrs={"class":"resp"})
           
           dur=element.find('span',attrs={"class":"film_duration"})
           if dur:
               try:
                   dur=str(int(dur.text.replace('min',''))*60)
               except:
                   dur=''
           if element.find('span',attrs={"class":"film_genre"}):
               gen=element.find('span',attrs={"class":"film_genre"}).text
           if element.find('span',attrs={"class":"film_production_year"}):    
               yr=element.find('span',attrs={"class":"film_production_year"}).text
           pl=element.find('p',attrs={"class":"short_desc"})
           if pl:
               pl=pl.text
           else:
               pl=''
           img=imgtag["src"]
           if title:
               title=title.text.strip()
           else:
               title=imgtag["alt"]
           
           if int(serie)==0:
#           Einzelfilm
                jsond=os.path.basename(link).replace('.html','.json')
                if os.path.isfile(temp+"/Filme/"+jsond):
                    with open(temp+"/Filme/"+jsond) as data_file:
                        filmdaten = json.load(data_file)
                else:
                    fd=geturl(link)
                    
                    FilmHtml = BeautifulSoup(fd, 'html.parser')
                    handlung=FilmHtml.find("div",attrs={'class':'handlungsblock'})
                    if handlung: 
                        pl=handlung.text.strip()
                    
                    f=FilmHtml.find('div',attrs={'id':'background-image'})
                    Bild=f.find('img',attrs={'class':'pdeatil-header-img'})
                    if Bild:
                        Fanart=Bild['src']
                    else:
                        Fanart=''
                    
                    Poster=''
                    Bilder=FilmHtml.find('div',attrs={'class':'media-swiper-holder'})
                    if Bilder:
                        Bild=Bilder.find_all('img')
                    else:
                        Bild=None
                    
                    if Bild:
                        for b in Bild:
                            if 'poster' in b['src'] or 'cover' in b['src']:
                                Poster=b['src']
                        
                    Zusatzinfos=FilmHtml.find('div',attrs={'class':'product-2nd-row'})
                    Darsteller=[]
                    if Zusatzinfos:
                        ds=Zusatzinfos.find('div',attrs={'class':'cast-link-actors'})
                        if ds: 
                            Darsteller=ds.find_all("a",attrs={'class':'alto'})
                        if not Darsteller:
                            Darsteller=[]
                        for i in range(len(Darsteller)):
                            Darsteller[i]=Darsteller[i].text
                        ds=Zusatzinfos.find('div',attrs={'class':'cast-link-directors'})
                        r=''
                        if ds:
                            r=ds.find_all("a",attrs={'class':'alto'})
                        Regie=''
                        if r:
                            for i in range(len(r)):
                                Regie+=r[i].text
                                if i<len(r)-1:
                                    Regie+=", "
                    
                    filmdaten={'Titel':title,'Link':link,'Dauer':dur,'Genre':gen,'Jahr':yr,'Plot':pl,'Darsteller':Darsteller,'Regie':Regie,'Poster':Poster,'Fanart':Fanart}
                    with io.open(temp+"/Filme/"+jsond, 'w', encoding='utf-8') as outfile:
                        outfile.write(json.dumps(filmdaten, ensure_ascii=False))

                addLink(filmdaten['Titel'],filmdaten['Link'],"playit",img,duration=filmdaten['Dauer'],genre=filmdaten['Genre'],year=filmdaten['Jahr'],desc=filmdaten['Plot'],cast=filmdaten['Darsteller'], poster=filmdaten['Poster'],director=filmdaten['Regie'],fanart=filmdaten['Fanart'])
           else:
                if genre==0:       
                    addDir(title,link,"getserie",img,serie=1)
                else:
                    addDir(title,link,"rubrik",img,serie=0)
           #<span class="film_production_year">2004</span> <span class="film_duration">114min</span>
        if htmlPage.find('a',attrs={"next i-next"}):
            page=int(page)+1
        else:
            weiter=False
       
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
    
        
def liste():
   addDir("Spielfilme","https://www.filmfriend.de/filme/spielfilme.html?dir=asc&order=name","rubrik","",serie=0,genre=0)
   addDir("Serien","https://www.filmfriend.de/filme/serien.html?dir=asc&order=name","rubrik","",serie=1,genre=0)   
   addDir("Genres","https://www.filmfriend.de/genres","rubrik","",serie=1,genre=1)      
   addDir("Beliebteste","https://www.filmfriend.de/beliebtestefilmfriend?dir=desc&order=review","rubrik","",serie=0,genre=0)
   addDir("Neue Filme","https://www.filmfriend.de/alle-filme?dir=desc&order=created_at","rubrik","",serie=0)
   addDir("Dokumentarfilme","https://www.filmfriend.de/filme/dokumentarfilme.html?dir=asc&order=name","rubrik","",serie=0)      
   addDir("Settings", "", 'Settings', "")
   xbmcplugin.endOfDirectory(addon_handle)
   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
page = urllib.unquote_plus(params.get('page', ''))
genre = urllib.unquote_plus(params.get('genre', ''))
serie = urllib.unquote_plus(params.get('serie', ''))
mpd = urllib.unquote_plus(params.get('mpd', ''))
key = urllib.unquote_plus(params.get('key', ''))

if not xbmcvfs.exists(cookie):
    login()

if mode is '':
     liste()   
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'playit':
          playit(url)
  if mode =="rubrik":
      rubrik(url,page,serie,genre)
  if mode == 'Settings':
          addon.openSettings()   
  if mode == 'getserie':
          getserie(url)
  if mode == 'playdash':
        playdash(mpd,key,url)
if delf==0:
    cj.save(cookie,ignore_discard=True, ignore_expires=True)
