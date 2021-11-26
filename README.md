# raramagnetica_pyIIIFpres

Test for using pyIIIFpres for rara magnetica project.

This test show how to use [pyIIIFpres](https://github.com/giacomomarchioro/pyIIIFpres) for creating mannifest compliant to IIIF presentation api 3.0.


## Installation
pyIIIFpres can be installed using `pip`:

    pip install git+https://github.com/giacomomarchioro/pyIIIFpres

Clone this repository using: 

    git clone https://github.com/giacomomarchioro/raramagnetica_pyIIIFpres.git
    
In the same folder of the python script must be present the imageurlist.txt (an orded list of all the ulrs of the images) and the metadata_v4.csv file of the same version of the script. 

To test the last version:

    python generatemanifestv4.py
