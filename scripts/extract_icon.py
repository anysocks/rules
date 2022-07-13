# coding = utf-8

import sys
import os
import pathlib
import peicon
import icoparser


def handle(f: str):
    p = pathlib.Path(f)
    icons_dir = os.path.join(os.path.dirname(__file__), '..', 'icons')
    extractor = peicon.IconExtractor(p)
    icon = extractor.get_icon()
    icon.seek(0)
    parser = icoparser.IcoParser.parse(icon.read())
    new_imgs = []
    for img in parser.images:
        print("spec: ", img.width, img.height, img.color_depth, img.bpp)
        if img.bpp != 32 or img.width < 16 or img.width > 64:
            print("^ REMOVED ^")
        else:
            new_imgs.append(img)
    parser.images = new_imgs

    # rebuild
    with open(os.path.join(icons_dir, "{}.ico".format(p.stem).lower()), 'wb') as fd:
        fd.write(parser.build())
    print("output: ", os.path.abspath(fd.name))


if __name__ == '__main__':
    handle(sys.argv[1])
