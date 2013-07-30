#!/usr/bin/env python

"""
ShotWell Web Gallery Export tool

Usage:
    swgallery [-hsv] [-t <target_directory>] [-a <author>] <event_name>

<event_name>                Name of the event.

Options:
    -h --help               Show this help message and exit.
    -s --show-time          Switch to show time in the description.
    -v --verbose            Enable verbose output.
    -q --quiet              No output at all.
    -t <target> --target=<target>
                            Define target directory where to export the web gallery
                            [default: ./gallery/].
    -a <author> --author=<author>
                            Define the author to attribute the works to
                            [default: Anonymous].
"""

import os
import sys
import shutil

import json
import docopt
import sqlite3
import traceback

from PIL import Image
from PIL.ExifTags import TAGS

from progress import Progress

WEBPAGE_TPL = """\
<html lang=en>
    <head>
        <title>{title}</title>
        <!-- link rel="stylesheet" href="rsrc/gallery.css" /-->
        <script src="rsrc/jquery-2.0.3.min.js"></script>
        <script src="rsrc/galleria.js"></script>
        <script>
            data = {data}
            Galleria.loadTheme('rsrc/galleria.classic.js');
            Galleria.run('#galleria', {{ dataSource: data,
                                        _toggleInfo: false,
                                            // extend: function(options) {{
                                            //     this.bind('image', function(e) {{
                                            //         $(e.imageTarget).click(this.proxy(function() {{
                                            //             this.openLightbox();
                                            //         }}));
                                            //     }});
                                            // }}
                                        }});
            Galleria.ready(function () {{
                $("#fullscreen").click(function () {{
                    $('#galleria').data('galleria').enterFullscreen()
                }});
            }});
        </script>
        <style>
            body      {{ background: #000000; color: #ffffff; }}
            header    {{ font-size: 20pt; }}
            #galleria {{ height: 90%; width: 100%; background: #000 }}
            .galleria-info-text {{ background: rgba(0,0,0,0.4)}}
            footer    {{ font-size: 8pt; text-align: center }}
            button    {{ background: #000000; color: #ffffff }}
        </style>
    </head>
    <body>
        <section id="galleria"></section>
        <footer>
            <button id="fullscreen">Fullscreen</button>
                <p class="cred">Made by {cred}.</p>
        </footer>
    </body>
</html>
"""

def export(event_name, targetdirectory = "gallery", jquery='jquery-2.0.3.min.js',
           show_time=False, author="Anonymous", verbose=False, db='~/.shotwell/data/photo.db'):

    db = sqlite3.connect(os.path.expanduser(db))

    gallery = []

    q = """\
    SELECT strftime("%Y/%m/%d", datetime(PhotoTable.exposure_time, "unixepoch")),
        EventTable.name, PhotoTable.filename, PhotoTable.title,
        PhotoTable.rating, strftime("%Hh%M", datetime(PhotoTable.time_created, "unixepoch"))
    FROM PhotoTable
    LEFT JOIN EventTable
            ON PhotoTable.event_id = EventTable.id
    WHERE EventTable.name=?"""

    cur = db.cursor()

    result = cur.execute(q, (event_name,)).fetchall()
    nbr, i = len(result), 0
    yield nbr

    for pic in result:
        i = i+1
        if pic[4] == 0:
            yield "[%5.1f%%]   Skip image (%d/5) %s/%s: %s\n" % (i/float(nbr)*100, pic[4], pic[0], pic[1], pic[2])
            continue
        basename = '.'.join(os.path.basename(pic[2]).split('.')[:-1])
        extension = os.path.basename(pic[2]).split('.')[-1]
        # create target directory
        d = os.path.join(targetdirectory, str(pic[0])) + '/'
        if not os.path.exists(d):
            os.makedirs(d)
        # create picture metadata
        descr = ""
        if show_time:
            descr = pic[5]
        if pic[3]:
            descr = descr + ", " if descr != "" else "" + str(pic[3]), # add tags
        else:
            descr = descr
        picture = dict(
            image = os.path.join('/', d, basename + '.' + extension),
            thumb = os.path.join('/', d, basename + '-sml.' + extension),
            big   = os.path.join('/', d, basename + '-big.' + extension),
            title = pic[1],
            description = descr,
            link  = os.path.join('/', d, basename + '.' + extension)
        )
        yield "[%5.1f%%] Create image (%d/5) %s/%s: %s" % (i/float(nbr)*100, pic[4], pic[0], pic[1], basename+'.'+extension)
        # copy image file
        if os.path.exists(str(pic[2])) and not os.path.exists(os.path.join(d, os.path.basename(pic[2]))):
            shutil.copyfile(pic[2], os.path.join(d, os.path.basename(pic[2])))
            # create thumbnail
            try :
                image = Image.open(os.path.join(d, os.path.basename(pic[2])))
                for orientation in TAGS.keys() :
                    if TAGS[orientation]=='Orientation' : break
                exif=dict(image._getexif().items())

                if   exif[orientation] == 3 :
                    image=image.rotate(180, expand=True)
                    image.save(os.path.join(d, os.path.basename(pic[2])))
                elif exif[orientation] == 6 :
                    image=image.rotate(270, expand=True)
                    image.save(os.path.join(d, os.path.basename(pic[2])))
                elif exif[orientation] == 8 :
                    image=image.rotate(90, expand=True)
                    image.save(os.path.join(d, os.path.basename(pic[2])))

                yield " ; thumbnail "
                for r in (0.1, 'sml'), (0.2, 'mdm'), (0.75, 'big'):
                    im2 = image.copy()
                    im2.thumbnail((int(image.size[0] * r[0]) , int(image.size[1] * r[0])), Image.ANTIALIAS)
                    im2.save(os.path.join(d, basename + '-{}'.format(r[1]) +
                                                    '.' + extension))
                    yield r[1] + " "
            except:
                traceback.print_exc()
        else:
            yield " ; does already exist, not overwritten"
        # append to gallery
        gallery.append(picture)
        yield " ; added to gallery.\n"

    # enable javascript stuff
    yield "Copying the resources.\n"
    if not os.path.exists(os.path.join(targetdirectory, 'rsrc')):
        os.makedirs(os.path.join(targetdirectory, 'rsrc'))

    pkg_dir = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib', jquery),
                    os.path.join(targetdirectory, 'rsrc', jquery))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib/galleria/src/galleria.js',),
                    os.path.join(targetdirectory, 'rsrc', 'galleria.js'))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib/galleria/src/themes/classic/galleria.classic.js',),
                    os.path.join(targetdirectory, 'rsrc', 'galleria.classic.js'))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib/galleria/src/themes/classic/galleria.classic.css',),
                    os.path.join(targetdirectory, 'rsrc', 'galleria.classic.css'))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib/galleria/src/themes/classic/classic-loader.gif',),
                    os.path.join(targetdirectory, 'rsrc', 'classic-loader.gif'))
    shutil.copyfile(os.path.join(pkg_dir, 'contrib/galleria/src/themes/classic/classic-map.png',),
                    os.path.join(targetdirectory, 'rsrc', 'classic-map.png'))

    yield "Creating index file...\n"
    # create index
    with open(os.path.join(targetdirectory, 'index.html'), 'w') as idx:
        idx.write(WEBPAGE_TPL.format(title=event_name,
                                 data=json.dumps(gallery),
                                 cred=author))

def run():
    options = docopt.docopt(__doc__)
    kwarg = dict()

    if options['--target']:
        kwarg['targetdirectory'] = options['--target']
    if options['--show-time']:
        kwarg['show_time'] = True
    if options['--author']:
        kwarg['author'] = options['--author']

    progress = None
    last = ""
    for msg in export(options['<event_name>'], **kwarg):
        if not options['--quiet']:
            if not progress:
                progress = Progress(msg)
                continue
            if options['--verbose']:
                sys.stdout.write(msg)
                sys.stdout.flush()
            else:
                if msg[0] == '[':
                    progress.increment()
                    last = msg.split(']')[1].strip()
                progress.print_status_line(last)



