#!/usr/local/bin/python
# coding: utf-8
from IIIFpres import iiifpapi3
import csv

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
rng.set_id(extendbase_url="range/r")
rng.add_label('en',"Tables of Contents")
strdic = {'base':rng}
with open('metadata_v2.csv') as csv_file, open('imageurllist.txt') as url_list:
    data = csv.DictReader(csv_file, delimiter=';')
    counter_rangel1 = 1
    counter_rangel2 = 1
    counter_rangel3 = 1

    for idx,d in enumerate(data):
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
        # some apsumptions there is always a structure parent of a subsection
        # fails when there are at the same time multiple structure and multiple subsections in the same page
        if d['structure'] != "":
            for i in d['structure'].split("\\"):
                stru_level1 = rng.add_range_to_items() 
                stru_level1.set_id(extendbase_url="range/r/%s" %counter_rangel1)
                counter_rangel1 +=1
                 # we reset the counter of level2
                counter_rangel2 = 0
                stru_level1.add_label('none',i)
                stru_level1.add_canvas_to_items(canvas_id=canvas.id)

        if d['sub_section'] != "":
            for j in d['sub_section'].split("\\"):
                stru_level2 = stru_level1.add_range_to_items() 
                stru_level2.set_id(extendbase_url="range/r/%s/%s" %(counter_rangel1,counter_rangel2))
                counter_rangel2 +=1
                # we reset the counter of level3
                counter_rangel3 = 0
                stru_level2.add_label('none',j)
                stru_level2.add_canvas_to_items(canvas_id=canvas.id)

        if d['subsub_section'] != "":
            for k in d['subsub_section'].split("\\"): 
                stru_level3 = stru_level2.add_range_to_items() 
                stru_level3.set_id(extendbase_url="range/r/%s/%s/%s" %(counter_rangel1,counter_rangel2,counter_rangel3))
                counter_rangel3 +=1
                stru_level3.add_label('none',k)
                stru_level3.add_canvas_to_items(canvas_id=canvas.id)


if __name__ == "__main__":
    manifest.json_save("manifest.json")