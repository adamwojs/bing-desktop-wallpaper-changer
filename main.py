#!/usr/bin/python
#-*- coding: utf-8 -*-

import getpass
import locale
import os
import re
import urllib
import urllib2

from bs4 import BeautifulSoup
import gtk


def get_valid_bing_markets():
    """
    Find valid Bing markets for area auto detection.

    :see: https://msdn.microsoft.com/en-us/library/dd251064.aspx
    :return: List with valid Bing markets (list looks like a list of locales).
    """
    url = 'https://msdn.microsoft.com/en-us/library/dd251064.aspx'
    page = urllib2.urlopen(url)
    page_xml = BeautifulSoup(page, 'lxml')
    # Look in the table data
    market = page_xml.find_all('td')
    market_locales = [el[1].text.strip() for el in enumerate(market) if
                      el[0] % 2 == 0]
    return market_locales


def get_bing_xml():
    """
    Get BingXML file which contains the URL of the Bing Photo of the day.

    :return: URL with the Bing Photo of the day.
    """
    # idx = Number days previous the present day.
    # 0 means today, 1 means yesterday
    # n = Number of images previous the day given by idx
    # mkt = Bing Market Area, see get_valid_bing_markets.
    market = 'en-US'
    default_locale = locale.getdefaultlocale()[0]
    if default_locale in get_valid_bing_markets():
        market = default_locale
    return "http://www.bing.com/HPImageArchive.aspx?format=xml&idx=0&n=1&mkt=%s" % market

BingXML_URL = get_bing_xml()
page = urllib2.urlopen(BingXML_URL)
BingXML = BeautifulSoup(page, "lxml")

# For extracting complete URL of the image
Images = BingXML.find_all('image')
BaseImage = Images[0].url.text
# Get appropriate screen resolution
window = gtk.Window()
screen = window.get_screen()
screen_size = r'%sx%s' % (gtk.gdk.screen_width(), gtk.gdk.screen_height())
# Replace image resolution with the correct resolution from your main monitor
CorrectResolutionImage = re.sub(r'\d+x\d+', screen_size, BaseImage)
ImageURL = "https://www.bing.com" + CorrectResolutionImage
ImageName = Images[0].startdate.text+".jpg"

# All the images will be saved in '/home/[user]/Pictures/BingWallpapers/'
username = getpass.getuser()
path = '/home/' + username + '/Pictures/BingWallpapers/'
if not os.path.exists(path):
    os.makedirs(path)
os.chdir(path)
if not os.path.isfile(ImageName):
    urllib.urlretrieve(ImageURL, ImageName)
    gsettings_path = os.system('which gsettings')
    if not os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri file:" + path + ImageName):
        os.system('notify-send "' + 'Bing Wallpaper updated successfully' +
                  '" "' + Images[0].copyright.text.encode('utf-8') + '"')
        os._exit(1)
else:
    os.system('notify-send "' + 'Bing Wallpaper unchanged' + '" "' +
              Images[0].copyright.text.encode('utf-8') + ' Wallpaper already exists in wallpaper directory!' + '"')
    os._exit(1)

os.system('notify-send "' + 'Failed to change Bing Wallpaper' +
          '" "' + "Please check the installation files again" + '"')
