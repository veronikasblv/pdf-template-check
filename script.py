#!/usr/bin/python

from sys import argv, version_info
import os
from PDFlib.TET import *

globaloptlist = ""
docoptlist = ""
pageoptlist = "granularity=line"

titlesize = 14
template_size = 10
template_font = "TimesNewRoman"
titlefont = "Bold"
template_width = 148
template_height = 210
texttrigger = "Аннотация"

pageno = 0

tet = TET()
if (version_info[0] < 3):
    fp = open(argv[2], 'w')
else:
    fp = open(argv[2], 'w', 2, 'utf-8')

directory = argv[1]
for fname in os.listdir(directory):
    f = os.path.join(directory, fname)
    if os.path.isfile(f) and f.endswith('.pdf'):

        tet.set_option(globaloptlist)
        doc = tet.open_document(f, docoptlist)
        n_pages = tet.pcos_get_number(doc, "length:pages")

        filename = f.split("\\")[-1]
        fp.write("\n- file: %s" % filename)

        width = round(tet.pcos_get_number(doc, "pages[%d]/width" % 0) * 25.4 / 72, 0)
        height = round(tet.pcos_get_number(doc, "pages[%d]/height" % 0) * 25.4 / 72, 0)
        if width != template_width or height != template_height:
            print("[Неверный формат страницы в %s: %dmm x %dmm]" % (filename, width, height))

        title = False
        by = False
        for pageno in range(1, int(n_pages) + 1):
            page = tet.open_page(doc, pageno, pageoptlist)

            text = tet.get_text(page)
            while (text != None and text != texttrigger):

                ci = tet.get_char_info(page)
                fontname = tet.pcos_get_string(doc, "fonts[%d]/name" % ci["fontid"])
                fontsize = round(ci["fontsize"], 0)

                if fontsize == titlesize and titlefont in fontname and template_font in fontname:
                    if not title:
                        title = True
                        fp.write("\n  title: " + text)
                    else:
                        fp.write(" " + text)
                elif fontsize == template_size and template_font in fontname and titlefont not in fontname:
                    author = text.split(",")[0]
                    if author[0].isupper() and author.count(".") == 2:
                        if not by:
                            by = True
                            fp.write("\n  by: " + author)
                        else:
                            fp.write(", " + author)
                else:
                    print("[Неверный шрифт в %s: %s %d] %s\n" % (filename, fontname, fontsize, text))

                text = tet.get_text(page)

            tet.close_page(page)
            if text == texttrigger:
                break
        tet.close_document(doc)
        fp.write("\n")

tet.delete()