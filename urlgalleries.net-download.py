#!/usr/bin/python3

import sys
import os
import argparse
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from parse import compile

url = 'http://moggy.urlgalleries.net/blog_gallery.php?id=4873870&g=Isabella_C_in_Diavgia'
dir = 'Isabella C in Diavgia'

def parse_baseurl_url_query(url_dirty):
    """Return the baseurl, url, and query."""
    parsed_url = urlparse(url_dirty)
    no_query = parsed_url._replace(query=None)

    baseurl = no_query._replace(path='/').geturl()
    url = no_query.geturl()
    query = parse_qs(parsed_url.query)
    return (baseurl, url, query)

def parse_baseurl(url):
    return urlparse(url)._replace(query=None, path='/').geturl()

p = compile("linkDestUrl = '{}';\n")

def get_img_src(url):
    _, url_clean, query = parse_baseurl_url_query(url)
    r = requests.get(url_clean, params=query)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'lxml')
    script = soup.body.script.string
    img_url = p.search(script)
    if img_url is None:
        return None
    else:
        img_url = img_url[0]

    baseurl, img_url, query = parse_baseurl_url_query(img_url)
    r = requests.get(img_url, params=query)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'lxml')
    img = soup.find('img', id='thepic')
    if img is None:
        return None
    img_src = img['src']

    return baseurl.rstrip('/') + '/' + img_src.lstrip('/')

def save_file(file_url, dir, file_name):
    pass

def get_images(url, dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    elif not os.path.isdir(dir):
        print("The path '{}' you specified is not a directory.".format(dir),
              file=sys.stderr)
        raise FileExistsError

    baseurl, url_clean, query = parse_baseurl_url_query(url)

    r = requests.get(url_clean, params=query)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'lxml')
    img_links = soup.find('td', attrs={'class': 'gallerybody'}).table.find_all('a')
    x = 1
    for img_link in img_links:
        url = baseurl.rstrip('/') + '/' + img_link['href'].lstrip('/')
        img_src = get_img_src(url)
        break
        if img_src is not None:
            ext = img_src.rsplit('.', 1)[-1]
            save_file(img_src, dir, '{name}.{ext}'.format(name=x, ext=ext))
            x += 1
        else:
            print(img_link)

def test():
    try:
        get_images(url, dir)
    except FileExistsError:
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='''Download images from
                                                    urlgalleries.net.''')
    parser.add_argument('url', metavar='url', type=str,
                        help='The URL from which to download images')
    parser.add_argument('-o', '--output', dest='output_folder', default='.')
    args = parser.parse_args()

    try:
        get_images(args.url, args.output_folder)
    except FileExistsError:
        sys.exit(1)

if __name__ == "__main__":
    test()
    #main()