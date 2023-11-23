#!/usr/bin/python

from sys import version_info #, argv
import os
from PDFlib.TET import *
from bs4 import BeautifulSoup as bs
from header import *

pageno = 0

argv = ["script.py", "spisok", "s.yml", "s.txt"]

tet = TET()
if version_info[0] < 3:
    fp = open(argv[2], 'w')
    fc = open(argv[3], 'w')
else:
    fp = open(argv[2], 'w', 2, 'utf-8')
    fc = open(argv[3], 'w', 2, 'utf-8')

directory = argv[1]
for fname in os.listdir(directory):
    f = os.path.join(directory, fname)
    if os.path.isfile(f) and f.endswith('.pdf'):
        title = False
        by = False
        abstract = False

        tet.set_option(globaloptlist)
        doc = tet.open_document(f, docoptlist)
        n_pages = tet.pcos_get_number(doc, "length:pages")

        filename = f.split("\\")[-1]
        fp.write("\n- file: %s" % filename)

        # page size check
        pixel_width = tet.pcos_get_number(doc, "pages[0]/width")
        pixel_height = tet.pcos_get_number(doc, "pages[0]/height")
        mm_width = to_mm(pixel_width)
        mm_height = to_mm(pixel_height)
        if mm_width != TEMPLATE_WIDTH or mm_height != TEMPLATE_HEIGHT:
            fc.write("\n[Неверный формат страницы (%dmm x %dmm) в %s]" % (mm_width, mm_height, filename))

        # metadata extraction
        page = tet.open_page(doc, 1, pageoptlist)
        text = tet.get_text(page)
        tet.close_page(page)

        paras = text.split('\u2029')
        for para in paras:
            if para == TEXTTRIGGER:
                break
            if not title:
                fp.write("\n  title: " + para.replace('\n', ' '))
                title = True
            else:
                para = para.replace(',', '\n')
                parts = para.split('\n')
                for part in parts:
                    if is_author(part):
                        if not by:
                            fp.write("\n  by: " + part)
                            by = True
                        else:
                            fp.write(", " + part)

        # margins and fonts
        for pageno in range(1, int(n_pages) + 1):

            page = tet.open_page(doc, pageno, pageoptlist)
            tet.process_page(doc, pageno, pageoptlist)
            tetml = tet.get_tetml(doc, "")
            soup = bs(tetml, 'xml')

            boxes = soup.find_all('Box')
            top_margin = to_mm(boxes[0]['ury'])
            bottom_margin = to_mm(pixel_height - float(boxes[-1]['lly']))

            # top margin
            tmcheck = TOP_MARGIN_TEMPLATE
            if pageno == 1:
                tmcheck = MARGIN_TEMPLATE
            if tmcheck - top_margin > DELTA or tmcheck - top_margin < 0:
                fc.write("\n[Неверный размер верхнего поля (%dmm) в %s (стр %d)]\n" % (top_margin, filename, pageno))

            # bottom margin
            if pageno == int(n_pages):
                if bottom_margin - MARGIN_TEMPLATE < 0:
                    fc.write("\n[Неверный размер нижнего поля (%dmm) в %s (стр %d)]\n" % (bottom_margin, filename, pageno))
            else:
                if bottom_margin - MARGIN_TEMPLATE > DELTA or bottom_margin - MARGIN_TEMPLATE < 0:
                    fc.write("\n[Неверный размер нижнего поля (%dmm) в %s (стр %d)]\n" % (bottom_margin, filename, pageno))

            # side margins and fonts
            tet.get_text(page)
            for box in boxes:
                left_margin = to_mm(box['llx'])
                right_margin = to_mm(pixel_width - float(box['urx']))
                para_texts = box.find_all("Text")
                for para_text in para_texts:
                    paragraph = para_text.string
                    if paragraph == ABSTRACT_END:
                        abstract = False
                    mcheck = MARGIN_TEMPLATE
                    if abstract:
                        mcheck = ABSTRACT_MARGIN

                    fonts = set()
                    for _ in range(len(paragraph)):
                        ci = tet.get_char_info(page)
                        if len(ci) > 0:
                            fontname = tet.pcos_get_string(doc, "fonts[%d]/name" % ci["fontid"])
                            fontsize = round(ci["fontsize"], 0)
                            fonts.add((fontname, fontsize))

                    margin_check = False
                    for font in fonts:
                        category = font_category(font[0], font[1])
                        if category is None:
                            fc.write("\n[Неверный шрифт (%s %d) в %s (стр %d)]: %s\n" % (font[0], font[1], filename,
                                                                                         pageno, paragraph))
                        if left_margin == right_margin and left_margin >= mcheck:
                            margin_check = True
                        elif (left_margin == mcheck or left_margin == mcheck + SIDE_DELTA) and right_margin >= mcheck:
                            margin_check = True

                    if not margin_check:
                        fc.write("\n[Неверный размер боковых полей (%d, %d) в %s (стр %d)]: %s\n"
                                 % (left_margin, right_margin, filename, pageno, paragraph))

                    if paragraph == TEXTTRIGGER:
                        abstract = True
                    ci = tet.get_char_info(page)

            tet.close_page(page)

        tet.process_page(doc, 0, "tetml={trailer}")
        tet.close_document(doc)
        fp.write("\n\n")
        fc.write("\n\n")

tet.delete()
