# -*- coding: utf-8 -*-
import hashlib
import os
from os import path
import re
import sqlite3
from sys import argv
import requests

import tinify
import leancloud
from leancloud import File

# Qiang 
import json
import glob

# TinyPng API key (link: https://tinypng.com/developers)
TINY_API_KEY = "set in main"

# LeanCloud API id & key (link: https://leancloud.cn/docs/python_guide.html)
LEAN_CLOUD_API_ID = "set in main"
LEAN_CLOUD_API_KEY = "set in main"

# Match image in Markdown pattern
INSERT_IMAGE_PATTERN = re.compile('(!\[.*?\]\((?!http)(.*?)\))', re.DOTALL)
INSERT_URL_PATTERN = re.compile(r'[^!]\[\]\((http.*?)\)')

URL_TITLE_PATTERN = re.compile(r'<title>(.*?)</title>')


# Init TinyPng and LeanCloud API
def init_api():
    tinify.key = TINY_API_KEY
    print("tinify.key: " + tinify.key)
    leancloud.init(LEAN_CLOUD_API_ID, LEAN_CLOUD_API_KEY)


def get_file_size(file_path):
    return float(path.getsize(file_path))


# Compress image by TinyPng (https://tinypng.com)
def compress(source, target):
    # print "compressing image %s, save to %s" % (source, target)
    data = tinify.from_file(source)
    data.to_file(target)
    scale = get_file_size(target) / get_file_size(source)
    return (1 - scale) * 100


# Upload image to LeanCloud
def upload(file_path):
    print(file_path)
    img_name = path.split(file_path)[1]
    with open(file_path, 'rb') as f:
        img_file = read_full_file(f) # Qiang
        up_file = File(img_name, buffer(img_file))
        up_file.save()
        img_url = up_file.url    
        return img_url


# Calculate image file hash value
def calc_hash(file_path):
    with open(file_path, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        file_hash = sha1obj.hexdigest()
        return file_hash


def connect_db(path):
    conn = sqlite3.connect(path)
    conn.execute('''
       CREATE TABLE IF NOT EXISTS ImageInfo(
       hash    TEXT    NOT NULL PRIMARY KEY,
       url     TEXT    NOT NULL
       );
    ''')
    return conn


def write_db(conn, img_hash, img_url):
    conn.execute("INSERT INTO ImageInfo (hash, url) VALUES ('%s','%s')" % (img_hash, img_url))
    conn.commit()


def find_in_db(conn, img_hash):
    cursor = conn.execute('SELECT * FROM ImageInfo WHERE hash=?', (img_hash,))
    return cursor.fetchone()


class Handler:
    def __init__(self):
        self.__content = ''

    def read_from(self, source):
        # with open(source) as md:    #python2
        with open(source, 'r', encoding='utf-8') as md:
            self.__content = md.read()
        return self

    def write_to(self, target):
        # with open(target, 'w') as md:    #python2
        with open(target, 'w', encoding='utf-8') as md:
            md.write(self.__content)

    def replace_image(self, db_path):
        images = INSERT_IMAGE_PATTERN.findall(self.__content)
        if not images:
            print('found no image reference in source file')
            return self

        # images = map(lambda i: i[1], images)    #python2
        images = list(map(lambda i: i[1], images))
        print('found %d image reference in source file' % len(images))

        with connect_db(db_path) as db:
            for image in images:
                if not path.exists(image):
                    print("can not find image %s :(" % image)
                    continue

                img_hash = calc_hash(image)
                # find database first
                image_data = find_in_db(db, img_hash)
                if image_data:
                    image_url = image_data[1]
                    print('[%s] => %s found in database' % (image, image_url))
                else:
                    # compress & upload
                    img_sp = path.split(image)
                    compressed_img = path.join(img_sp[0], 'cp_' + img_sp[1])
                    size_percent = compress(image, compressed_img)
                    image_url = upload(compressed_img).encode('utf-8')
                    write_db(db, img_hash, image_url)
                    print('[%s] => %s , size ⬇ %.2f%%' % (image, image_url, size_percent))
                    os.remove(compressed_img) # delete copy img, Qiang
                self.__content = self.__content.replace('(%s)' % image, '(%s)' % str(image_url))
        print

        return self

    def replace_url(self):
        urls = INSERT_URL_PATTERN.findall(self.__content)
        if not urls:
            print('found no url reference in source file')
            return self

        print('found %d url reference in source file' % len(urls))
        for url in urls:
            try:
                # download html & extract title
                title = URL_TITLE_PATTERN.search(requests.get(url, timeout=5).text)
                title = title.group(1).encode('utf-8') if title else ''

                self.__content = self.__content.replace('[](%s)' % url, '[%s](%s)' % (title, url))
                print('[%s] => %s' % (url, title))
            except:
                print('[%s] replace failed :(' % url)
        print

        return self




# set all keys, Qiang
def set_keys(script):
    # f = file(os.path.join(os.path.split(script)[0], "key.json"))   # python2
    f = open(os.path.join(os.path.split(script)[0], "key.json"), 'r',encoding='utf=8')    #python3
    j = json.load(f)
    global TINY_API_KEY
    global LEAN_CLOUD_API_ID
    global LEAN_CLOUD_API_KEY
    TINY_API_KEY = j["tiny_api_key"]
    LEAN_CLOUD_API_ID = j["lean_cloud_api_id"]
    LEAN_CLOUD_API_KEY = j["lean_cloud_api_key"]
    f.close


# for full read file on Windows, Qiang
def read_full_file(file):
	data = ''
	while True:
		s = file.read()
		if len(s) == 0:
			return data
		data = data + s


# find md, Qiang
def get_source_md():
    path = os.getcwd()
    files = glob.glob(path + "\\*.md")
    for file in files:
        filename = os.path.basename(file)
        print("filename: " + filename)
        return file, filename
        

# do in current dir, Qiang
def deal_in_curr_dir(argv):
        script_file = argv[0]
        source_file, filename = get_source_md()
        if source_file:
            main(script_file, source_file, "../../_posts/" + filename)
        else:
            print('can not find .md in current dir')






def main(script, source, target):
    if not path.exists(source):
        print("source file doesn't exist :(")
        return

    set_keys(script)
    init_api()

    Handler() \
        .read_from(source) \
        .replace_image(os.path.join(os.path.split(script)[0], "ImageInfo.db")) \
        .replace_url() \
        .write_to(target)

    print('all done')


if __name__ == '__main__':
    if len(argv) == 1:
        deal_in_curr_dir(argv)
    elif len(argv) > 2:
        script_file, source_file, target_file = argv
        main(script_file, source_file, target_file)
    else:
        print('please enter source file and target file')
