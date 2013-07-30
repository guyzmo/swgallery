Web Gallery Export Tool for Shotwell
====================================

INSTALL
-------

when I'll have it uploaded on pipy, you will be able to install it through:

    pip install swgallery

meanwhile, you need to install it manually:

    git clone --recursive https://github.com/guyzmo/swgallery.git
    cd swgallery
    python setup.py install

DEPENDS ON
----------

  * uses [galleria.js](http://galleria.io) to render the gallery (MIT License)
  * uses a progress library (Python license) from Tim Newsome
  * uses Python Image Library to manipulate images


DEVELOP
-------

You'll need `zc.buildout` (that you can install through `pip install zc.buildout`)

    git clone --recursive https://github.com/guyzmo/swgallery.git
    cd swgallery
    buildout

LICENSE
-------

All original work is under AGPLv3


