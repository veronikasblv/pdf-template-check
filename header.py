def is_author(text):
    words = text.split()
    up_let = True
    dot = False
    for word in words:
        if len(word) < 2:
            up_let = False
            break
        elif not (word[0].isupper() or word[1].isupper()):
            up_let = False
            break
        if word[-1] == ".":
            dot = True
    return dot and up_let

def to_mm(pixels):
    return round(float(pixels) * 25.4 / 72, 0)

def font_category(fontname, fontsize):
    if "TimesNewRoman" in fontname:
        if "Bold" in fontname and (fontsize == 14 or fontsize == 12 or fontsize == 11):
            return "TITLE"
        if fontsize == 10:
            return "DEFAULT"
        if fontsize == 9:
            return "CAPTION"
        if fontsize == 8:
            return "THANKS"
        if fontsize == 7 or fontsize == 6:
            return "SUP"
    if "Courier" in fontname and fontsize == 8:
        return "LISTING"
    if "Arial" in fontname and fontsize == 10:
        return "FORMULA"
    return None

globaloptlist = ""
docoptlist = "tetml = {elements={annotations=false attachments=false bookmarks=false destinations=false" \
             " docinfo=false fields=false javascripts=false metadata=false options=false}} paraseparator=U+2029"
pageoptlist = "granularity=page topdown={output} structureanalysis={list=false}"


TEMPLATE_WIDTH = 148
TEMPLATE_HEIGHT = 210
TEXTTRIGGER = "Аннотация"
ABSTRACT_END = "Введение"
TOP_MARGIN_TEMPLATE = 23
MARGIN_TEMPLATE = 17
ABSTRACT_MARGIN = MARGIN_TEMPLATE + 10
LISTING_MARGIN = MARGIN_TEMPLATE + 5

DEFAULT_FONTSIZE = 10
DELTA = to_mm(DEFAULT_FONTSIZE * 4 / 3)