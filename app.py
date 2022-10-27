import os
import base64
from re import S
import sys
import json
import config
import requests
import urllib.request

from bs4 import BeautifulSoup

from Class.JJFPost import JJFPost

REG_COUNTER = 0
PHOTO_COUNTER = 0
TP = 0
TPE = 0
TV = 0
TVE = 0
TT = 0
TTE = 0


def create_folder(tpost, type=False):
    global REG_COUNTER
    global PHOTO_COUNTER

    if (type):
        counter = PHOTO_COUNTER
    else:
        counter = REG_COUNTER

    fpath = os.path.join(config.save_path, tpost.name, tpost.type,
                         f'{counter}' + "_" + tpost.post_date)

    if not os.path.exists(fpath):
        os.makedirs(fpath)

    if (type):
        PHOTO_COUNTER += 1
    else:
        REG_COUNTER += 1

    return fpath


def photo_save(ppost):
    ii = 1
    photos_url = []

    photos_img = ppost.post_soup.select(
        'div.imageGallery.galleryLarge img.expandable')

    if len(photos_img) == 0:
        ii = -1
        photos_img.append(ppost.post_soup.select('img.expandable')[0])

    global PHOTO_COUNTER, TP, TPE
    PHOTO_COUNTER = 0
    folder = create_folder(ppost)

    for img in photos_img:
        print(f'img: {img}')
        try:
            imgsrc = img.attrs['data-lazy']
        except KeyError:
            print("No data-lazy")
            try:
                imgsrc = img.attrs['src']
            except KeyError:
                print("No src")
                print(f'{img}')
                TPE += 1
                return

        ext = imgsrc.split('.')[-1]

        ppost.photo_seq = ii
        ppost.ext = ext
        ppost.prepdata()
        ppath = os.path.join(folder, ppost.title)

        if not config.overwrite_existing and os.path.exists(ppath):
            print(f'p: <<exists skip>>: {ppath}')
            ii += 1
            TP += 1
            continue

        photos_url.append([ppath, imgsrc, ppost.ext, ppost.name])

        ii += 1

        print(f'p: {ppath}')
        TP += 1

    for img in photos_url:
        #urllib.request.urlretrieve(img[1], img[0])
        r = requests.get(img[1])
        with open(img[0], 'wb') as outfile:
            outfile.write(r.content)


def video_save(vpost):
    vpost.ext = 'mp4'
    vpost.prepdata()

    folder = create_folder(vpost)
    vpath = os.path.join(folder, vpost.title)

    global TV, TVE

    if not config.overwrite_existing and os.path.exists(vpath):
        print(f'v: <<exists skip>>: {vpath}')
        TV += 1
        return

    try:
        vidurljumble = vpost.post_soup.select(
            'div.videoBlock a')[0].attrs['onclick']
    except:
        print(f'No video')
        TVE += 1
        return

    vidurl = json.loads(vidurljumble.split(', ')[1])

    vpost.url_vid = vidurl.get('1080p', '')
    vpost.url_vid = vidurl.get('540p',
                               '') if vpost.url_vid == '' else vpost.url_vid

    print(f'v: {vpath}')
    TV += 1

    urllib.request.urlretrieve(vpost.url_vid, vpath)


def text_save(tpost):
    tpost.ext = 'txt'
    tpost.prepdata()

    folder = create_folder(tpost)
    tpath = os.path.join(folder, tpost.title)

    global TT, TTE

    if not config.overwrite_existing and os.path.exists(tpath):
        print(f't: <<exists skip>>: {tpath}')
        TT += 1
        return

    print(f't: {tpath}')
    TT += 1

    text_file = open(tpath, "w", encoding='utf-8')
    text_file.write(tpost.full_text)
    text_file.close()


def parse_and_get(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # name
    name = soup.select('h5.mbsc-card-title.mbsc-bold span')[0].text
    # date
    post_date = soup.select('div.mbsc-card-subtitle')[0].text.strip()

    for pp in soup.select('div.mbsc-card.jffPostClass'):

        ptext = pp.select('div.fr-view')

        thispost = JJFPost()
        thispost.post_soup = pp
        thispost.name = name
        thispost.post_date_str = post_date.strip()
        thispost.post_id = pp.attrs['id']
        thispost.full_text = ptext[0].text.strip() if ptext else ''
        thispost.prepdata()

        classvals = pp.attrs['class']
        global REG_COUNTER
        if 'video' in classvals:
            print('VIDEO ...')
            thispost.type = 'video'
            video_save(thispost)
            REG_COUNTER -= 1
            if config.save_full_text:
                #thispost.type = 'text'
                text_save(thispost)
            print('.........')

        if 'photo' in classvals:
            print('PHOTO ...')
            thispost.type = 'photo'
            photo_save(thispost)
            REG_COUNTER -= 1
            if config.save_full_text:
                #thispost.type = 'text'
                text_save(thispost)
            print('.........')

        elif 'text' in classvals:
            print('TEXT  ...')
            if config.save_full_text:
                thispost.type = 'text'
                text_save(thispost)
            print('.........')


if __name__ == "__main__":
    uid = sys.argv[1]
    hsh = sys.argv[2]

    api_url = config.api_url

    loopit = True
    loopct = 0
    while loopit:

        geturl = api_url.format(userid=uid, seq=loopct, hash=hsh)
        html_text = requests.get(geturl).text

        if 'as sad as you are' in html_text:
            loopit = False
        else:
            parse_and_get(html_text)
            loopct += 10

    print(f'Total photos | Errors: {TP} | {TPE}')
    print(f'Total text | Errors: {TT} | {TTE}')
    print(f'Total videos | Errors: {TV} | {TVE}')
