#!/usr/local/bin/python
# coding: utf-8
from IIIFpres import iiifpapi3
import csv
from collections import defaultdict
import requests

iiifpapi3.BASE_URL = "https://dlib.biblhertz.it/iiif/bncrges1323/" # this is the path where the manifest must be accessible
# some of the resources use @ which might be cause conflict we ignore the error
iiifpapi3.INVALID_URI_CHARACTERS = iiifpapi3.INVALID_URI_CHARACTERS.replace("@","")
manifest = iiifpapi3.Manifest()
manifest.set_id(extendbase_url="manifest.json")
manifest.add_label("en","Zucchi, Philosophia magnetica") # it'is eng?
manifest.add_behavior("paged")
manifest.add_behavior("continuous")
manifest.set_navDate("2021-11-16T18:17:44.573+01:00")
manifest.set_rights("http://creativecommons.org/licenses/by-nc/4.0/")
manifest.set_requiredStatement(label="Attribution",language_l="en",value="Provided by BHMPI Rome",language_v="en")
manifest.add_metadata(label="author", value="Niccolò Zucchi", language_l="en", language_v="en")
manifest.add_metadata(label="title", value="Philosophia magnetica per principia propria proposita et ad prima in suo genere promota", language_l="en", language_v="none")
manifest.add_metadata(label="date", value="c. 1653", language_l="en", language_v="none")
manifest.add_metadata(label="held by", value="Rom, Biblioteca Nazionale Centrale Vittorio Emanuele II", language_l="en", language_v="none")
manifest.add_metadata(label="shelfmark", value="Fondo Gesuitico 1323, fols. 59r–78r", language_l="en", language_v="none")
manifest.add_metadata(label="catalogue", value="<a href=\"http://aleph.mpg.de/F/?func=find-b&local_base=kub01&find_code=idn&request=BV0000000\">Kubikat </a>", language_l="en", language_v="none")
manifest.add_metadata(label="hosted by", value="<span><a href=\"https://www.biblhertz.it\">BHMPI Rome</a></span>", language_l="en", language_v="none")
manifest.add_metadata(label="part of", value="<span><a href=\"https://ch-sander.github.io/raramagnetica/\">rara magnetica</a> by Christoph Sander</span>", language_l="en", language_v="none")
manifest.add_metadata(label="identifier", value="ark:/30440/02/bncrges1323", language_l="en", language_v="none")


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


manifest.structures = []
rng = manifest.add_range_to_structures()
rng.set_id(extendbase_url="range/")
rng.add_label('en',"Tables of Contents")
strdic = {0:rng}
last_label = None
rngind = defaultdict(int)
idx = 0
with open('metadata_v4.csv') as csv_file, open('imageurllist.txt') as url_list:
    data = csv.DictReader(csv_file, delimiter=',')
    lastlevel = 1
    for d in data:
        if d['canvas label'] != last_label:
            last_label = d['canvas label']
            idx+=1 
            # when you use a proxy you might have to use the original link e.g. "http://localhost:1080/iipsrv/iipsrv.fcgi?iiif=/imageapi//m0171_0/m0171_0visn20_0001a21.jp2/info.json"
            iiifimageurl = next(url_list).strip() 
            imageinfo =  requests.get(iiifimageurl,verify=False) 
            jsoninfo = imageinfo.json()
            imgwidth = jsoninfo['width']
            imgheight = jsoninfo['height']
            canvas = manifest.add_canvas_to_items()
            canvas.set_id(extendbase_url="canvas/p%s"%idx) # in this case we use the base url
            canvas.set_height(imgheight) # this can be retrieved from the images or using image api
            canvas.set_width(imgwidth) # this can be retrieved from the images or using image api
            canvas.add_label("en",d['canvas label'])
            annopage = canvas.add_annotationpage_to_items()
            annopage.set_id(extendbase_url="page/p%s/1" %str(idx).zfill(4))
            annotation = annopage.add_annotation_to_items(target=canvas.id)
            annotation.set_id(extendbase_url="annotation/p%s-image"%str(idx).zfill(4))
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
        if d['structure'] != "":
            if d['level'] == "":
                raise ValueError("Plase specify a level for: %s, %s" %(d['structure'],d['canvas label']))
            currentlevel = int(d['level'])
            if currentlevel < lastlevel: # this is the case of a new chapter
                for lv in list(rngind):
                    if lv > currentlevel:
                        del rngind[lv] # we have to reset the counters
            lastlevel = currentlevel  
            rngind[currentlevel] +=1 
            previouslevel = currentlevel - 1
            strdic[currentlevel] = strdic[previouslevel].add_range_to_items()
            currentpath = "/".join(["r%s"%rngind[i] for i in sorted(rngind)])
            strdic[currentlevel].set_id(extendbase_url="range/"+currentpath)
            strdic[currentlevel].add_label('none',d['structure'])
            strdic[currentlevel].add_canvas_to_items(canvas_id=canvas.id)


if __name__ == "__main__":
    manifest.json_save("manifest.json")
