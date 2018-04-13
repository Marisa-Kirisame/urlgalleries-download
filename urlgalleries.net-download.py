#!/usr/bin/python3

import sys
import os
import argparse
import glob
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup
from parse import compile

force = False

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

    return urljoin(baseurl, img_src)

def save_file(url, file_name):
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()

    with open(file_name, 'wb') as file_:
        file_.write(r.content)

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
    for x, img_link in enumerate(img_links, 1):
        if not force and glob.glob(os.path.join(dir, '{}.*'.format(x))):
            continue

        url = urljoin(baseurl, img_link['href'])
        try:
            img_src = get_img_src(url)
        except KeyboardInterrupt:
            raise
        except:
            print('Error: ' + img_link['href'])
        if img_src is not None:
            ext = img_src.rsplit('.', 1)[-1]
            file_name = os.path.join(dir, str(x) + '.' + ext)
            save_file(img_src, file_name)
            print(file_name)
        else:
            print('Error: ' + img_link['href'])

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
    parser.add_argument('-o', '--output', dest='output_folder', default='.',
                        help='The output directory. Default is the current directory')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force overwriting image files')
    args = parser.parse_args()

    if args.force:
        global force
        force = True

    try:
        get_images(args.url, args.output_folder)
    except FileExistsError:
        sys.exit(1)

if __name__ == "__main__":
    #test()
    main()
