import json
from datetime import datetime
from sys import argv, exit, stderr
from time import mktime

if len(argv) != 2:
    stderr.write("Usage: python cream.py <path-to-file-to-convert>\n")
    exit(-1)

in_name = 'Bookmarks.bak'
with open(in_name, 'r') as f:
    data = f.read()
for c in ('\t', '\r', '\n'):
    data = data.replace(c, '')

# Get data into a dict (well, JSON format)
obj = json.loads(data)
outer_keys = obj.keys() # should be at least 'checksum', 'version', and 'roots'

roots = obj['roots']
roots_keys = roots.keys()   # should be at least 'synced', 'sync_transaction_version',
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

newdate = datetime(1970, 6, 9, 4, 20)
datestr = int(mktime(newdate.timetuple()))
dir_line_template = """<DT><H3 ADD_DATE=\"%s\" LAST_MODIFIED=\"%s\"%s>%s</H3>"""
url_line_template = """<DT><A HREF=\"%s\" ADD_DATE=\"%s\">%s</A>"""

def print_file_header():
    header = """\
    <!DOCTYPE NETSCAPE-Bookmark-file-1>
    <!-- This is an automatically generated file.
    It will be read and overwritten. DO NOT EDIT! -->
    <META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
    <DL><p>
    """

    header = header.replace("    ", '') # remove indentation before printing
    print header,

def traverse_dir(dir_dict, indent=0, root=False):
    # TODO use real dates
    name = dir_dict['name']
    name = name.replace("<", "&lt;")
    name = name.replace(">", "&gt;")
    date_added, date_modded = datestr, datestr
    indent_str = "    " * indent
    root_str = """PERSONAL_TOOLBAR_FOLDER=\"true\"""" if root else ""
    dir_line = dir_line_template % (date_added, date_modded, root_str, name)
    print indent_str + dir_line
    print indent_str + "<DL><p>"

    children = dir_dict['children']
    for c in children:
        if c['type'] == u'folder':
            traverse_dir(c, indent + 1)
        else:
            url, url_name = c['url'], c['name']
            url_name = url_name.replace("<", "&lt;")
            url_name = url_name.replace(">", "&gt;")
            url_date_added = datestr
            url_line = url_line_template % (url, url_date_added, url_name)
            url_indent = indent_str + "    "
            print url_indent + url_line.encode('utf-8')
    print indent_str + "</DL><p>"

def print_other_bookmarks():
    if 'other' not in obj.keys():
        return
    other_dict = obj['other']
    for c in other_dict['children']:
        if c['type'] == 'folder':
            traverse_dir(c, 2)
        else:
            url, url_name = c['url'], c['name']
            url_date_added = datestr
            url_line = url_line_template % (url, url_date_added, url_name)
            url_indent = " " * 8
            print url_indent + url_line

print_file_header()
traverse_dir(bookmarks_root, indent=1, root=True)
print_other_bookmarks()
print "</DL><p>" # file footer
