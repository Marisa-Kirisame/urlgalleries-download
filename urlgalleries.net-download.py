#!/usr/bin/python3

import sys
import argparse
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

TEST = True
#TEST = False

url = 'http://moggy.urlgalleries.net/blog_gallery.php?id=4873870&g=Isabella_C_in_Diavgia'
dir = 'Isabella C in Diavgia'

debug_args = [url, '-o', dir]

def get_images(url_dirty, output_folder):
    url_dirty = 'http://moggy.urlgalleries.net/blog_gallery.php?id=4873870&g=Isabella_C_in_Diavgia'
    o = urlparse(url_dirty)
    query = parse_qs(o.query)
    url = o._replace(query=None).geturl()

    r = requests.get(url, params=query)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    soup = BeautifulSoup(r.text, 'lxml')
    imgs = soup.find('td', attrs={'class': 'gallerybody'}).table.find_all('img')
    for img in imgs:
        print(img['src'])

"""
This is 1st paragraph text.
2nd line also include text text text.
3rd line include text text text.
"""

def test():
    get_images(url, dir)

def main():
    parser = argparse.ArgumentParser(description='''Download images from
                                                    urlgalleries.net.''')
    parser.add_argument('url', metavar='url', type=str,
                        help='The URL from which to download images')
    parser.add_argument('-o', '--output', dest='output_folder', default='.')
    args = parser.parse_args()

    get_images(args.url, args.output_folder)

if __name__ == "__main__":
    if TEST:
        test()
    else:
        main()
