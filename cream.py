import json
from datetime import datetime
from sys import argv, exit
from time import mktime

# (Pls use the program correctly!)
if len(argv) != 2:
    exit("Usage: python cream.py <path-to-file-to-convert>\n")

in_name = argv[1]
with open(in_name, 'r') as f:
    data = f.read()
for c in ('\t', '\r', '\n'):
    data = data.replace(c, '')

# Get data into a dict (well, JSON format)
obj = json.loads(data) # keys of this dict should be at least 'checksum', 'version', and 'roots'

roots = obj['roots']   # keys should be at least 'synced', 'sync_transaction_version',
                       # 'bookmark_bar', and maybe 'other' for 'other bookmarks' folder

bookmarks_root = roots['bookmark_bar']

# Here we go, a directory structure. Every directory has 6 attributes:
#   id      name          children
#   type    date_added    date_modified
#
# All attributes except for 'children' just have a Unicode string value. 'type' is just the Unicode
# string, u'folder' (big surprise, right?). The dates have a format I don't recognize. 'children' 
# has a list of objects that each represent a directory or a bookmarked link. 
#
# Oh, speaking of which, a link has these 6 attributes (sometimes the last one here is omitted):
#   id      name          url
#   type    date_added    meta_info
#
# The attributes 'id', 'date_added', and 'name' are the same as before. 'url' is a Unicode string
# representing a URL. 'type' just has the Unicode string, u'url'. If present, the attribute 
# meta_info contains an object with at least 1 attribute, 'last_visited_desktop' which maps to a
# Unicode string representing a date. In only one case, I have seen other attributes like
# 'stars.id', 'stars.imageData', and others starting with 'stars'. I don't know what it represents,
# but it seems unimportant so I'm skipping it.
#
# Sometimes, a URL will have a 'sync_transaction_version' attribute. I don't know why. But it's not
# used, anyway, so I'm ignoring it in this code.

# Anyway, now to convert the file...
# Need templates for print statements later
dir_line_template = """<DT><H3 ADD_DATE=\"%s\" LAST_MODIFIED=\"%s\"%s>%s</H3>"""
url_line_template = """<DT><A HREF=\"%s\" ADD_DATE=\"%s\">%s</A>"""

def getdate(date_num):
    """
    Convert a date given from the bookmarks file to a legit date.

    Interestingly enough, the dates in that file use Jan 1, 1601 as the epoch. Which is 369 years
    off from the Unix epoch of 1/1/1970. So we need to take the number and remove 369 years from it.
    """
    # First convert to seconds from microseconds though.
    date_num = long(date_num)
    date_num /= 1000000
    date_num -= (369*365*24*60*60 + 24*60*60*89) # You are welcome to figure out what the 89
                                                 # means. I have not figured it out myself. Doesn't
                                                 # seem like it stands for leap year days. But it
                                                 # makes the formula work...
    # Anyway we now have seconds since the epoch so return this
    return date_num

def print_file_header():
    """This will print the stuff that goes at the top of the HTML file."""

    header = """\
    <!DOCTYPE NETSCAPE-Bookmark-file-1>
    <!-- This is an automatically generated file.
    It will be read and overwritten. DO NOT EDIT! -->
    <META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
    <DL><p>\
    """
    header = header.replace("    ", '') # remove indentation before printing it
    print header

def print_url(url_dict, indent_str):
    """Print a given URL, given as a dict."""
    url, url_name = url_dict['url'], url_dict['name']
    url_name = url_name.replace("<", "&lt;").replace(">", "&gt;")
    url_date_added = getdate(url_dict['date_added'])
    url_line = url_line_template % (url, url_date_added, url_name)
    url_indent = indent_str + "    "
    print url_indent + url_line.encode('utf-8')

def traverse_dir(dir_dict, indent=0, root=False):
    """
    Will parse a JSON directory object and print the appropriate URLs and bookmark (sub)folders.
    """
    name = dir_dict['name']
    name = name.replace("<", "&lt;").replace(">", "&gt;")
    date_added, date_modded = getdate(dir_dict['date_added']), getdate(dir_dict['date_modified'])
    indent_str = "    " * indent
    root_str = """PERSONAL_TOOLBAR_FOLDER=\"true\"""" if root else ""
    dir_line = dir_line_template % (date_added, date_modded, root_str, name)
    print indent_str + dir_line
    print indent_str + "<DL><p>"

    children = dir_dict['children']
    for c in children:
        if c['type'] == 'folder':
            traverse_dir(c, indent + 1)
        else:
            print_url(c, indent_str)
    print indent_str + "</DL><p>"

def print_other_bookmarks():
    """Deal with the bookmarks in the "Other Bookmarks" folder, if any."""
    if 'other' not in obj.keys():
        return
    other_dict = obj['other']
    for c in other_dict['children']:
        if c['type'] == 'folder':
            traverse_dir(c, 2)
        else:
            print_url(c, "    ")

print_file_header()
traverse_dir(bookmarks_root, indent=1, root=True)
print_other_bookmarks()
print "</DL><p>" # file footer
