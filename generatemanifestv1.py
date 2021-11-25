#!/usr/local/bin/python
# coding: utf-8
from IIIFpres import iiifpapi3
import csv

import requests

iiifpapi3.BASE_URL = "https://dlib.biblhertz.it/iiif/enap124300/"
# some of the resources use @ which might be cause conflict we ignore the error
iiifpapi3.INVALID_URI_CHARACTERS = iiifpapi3.INVALID_URI_CHARACTERS.replace("@","")
manifest = iiifpapi3.Manifest()
manifest.set_id(extendbase_url="manifest.json")
manifest.add_label("en","bncrges1323")
manifest.add_behavior("paged")
manifest.add_behavior("continuous")
manifest.set_navDate("2021-11-16T18:17:44.573+01:00")
manifest.set_rights("http://creativecommons.org/licenses/by-nc/4.0/")
manifest.set_requiredStatement(label="Attribution",language_l="en",value="Provided by BHMPI Rome",language_v="en")
manifest.add_metadata(label="title", value="[Drawings Of Naples, & c.]", language_l="en", language_v="en")


prov = manifest.add_provider()
prov.set_id("https://www.biblhertz.it/en/mission")
prov.set_type()
prov.add_label(language='en',text="Bibliotheca Hertziana – Max Planck Institute for Art History")
homp = prov.add_homepage()
homp.set_id("https://www.biblhertz.it/")
homp.set_type("Text")
homp.add_label("en","Bibliotheca Hertziana")
homp.set_format("text/html")
homp.set_language("en")
logo = prov.add_logo()
logo.set_id("https://dlib2.biblhertz.it/iiif/3/rsc@bhmpi.jp2/full/200,/0/default.jpg")
serv = logo.add_service()
serv.set_id("https://dlib2.biblhertz.it/iiif/3/rsc@bhmpi.jp2")
serv.set_type("ImageService3")
serv.set_profile("level2")
start = manifest.set_start()
start.set_id("https://dlib2.biblhertz.it/iiif/3/bncrges1323/canvas/p0005") # this must be provided
start.set_type("Canvas")

with open('metadata_v1.csv') as csv_file:
    data = csv.reader(csv_file, delimiter=',')

    for idx,d in enumerate(data):
        idx+=1 
        # when you use a proxy you might have to use the original link e.g. "http://localhost:1080/iipsrv/iipsrv.fcgi?iiif=/imageapi//m0171_0/m0171_0visn20_0001a21.jp2/info.json"
        iiifimageurl = "https://dlib2.biblhertz.it/iiif/3/bncrges1323@0001.jp2" 
        imageinfo =  requests.get(iiifimageurl,verify=False) 
        jsoninfo = imageinfo.json()
        imgwidth = jsoninfo['width']
        imgheight = jsoninfo['height']
        canvas = manifest.add_canvas_to_items()
        canvas.set_id(extendbase_url="canvas/p%s"%idx) # in this case we use the base url
        canvas.set_height(imgheight) # this can be retrieved from the images or using image api
        canvas.set_width(imgwidth) # this can be retrieved from the images or using image api
        canvas.add_label("en",d[1])
        annopage = canvas.add_annotationpage_to_items()
        annopage.set_id(extendbase_url="page/p%s/1" %d[0])
        annotation = annopage.add_annotation_to_items(target=canvas.id)
        annotation.set_id(extendbase_url="annotation/p%s-image"%d[0].zfill(4))
        annotation.set_motivation("painting")
        annotation.body.set_id("".join((iiifimageurl,"/full/max/0/default.jpg"))) # this will be the url
        annotation.body.set_type("Image")
        annotation.body.set_format("image/jpeg")
        annotation.body.set_width(imgwidth) # this can be retrieved from the images or using image api
        annotation.body.set_height(imgheight) # this can be retrieved from the images or using image api
        s = annotation.body.add_service()
        s.set_id(iiifimageurl) # this will be the url
        s.set_type("ImageService3")
        s.set_profile("level1")
if __name__ == "__main__":
    manifest.json_save("manifest.json")