# Cream

A quick Python 2 script to turn a Bookmarks or Bookmarks.bak file from Google Chrome into an HTML
file that Chrome can import. (WINDOWS ONLY)

## Why?

Sometimes, Chrome might accidentally wipe your bookmarks bar and delete all of your bookmarked
links. (That just happened to me. Guess why I wrote this???) While Chrome _does_ save your bookmarks
to your computer, the file containing your bookmarks is not formatted in such a way that Chrome can
import it and restore the bookmarks from that file. This script converts such a bookmarks file to 
that format.

Chrome saves bookmarks into two files. One is just called 'Bookmarks', and the other is
'Bookmarks.bak'. As its name implies, the second file is a backup file (although I'm unsure what the
backup schedule is, exactly; I did see a gap of 10 hours between the modification times of each
file, on the same day that Chrome recently wiped my bookmarks: 1:30AM for the .bak file and about
11:30AM for the non-.bak file). 

## Technical deets

Each file is actually just formatted in JSON, as one big object. It looks sort of like this:
```
{
    'checksum': 'some hex value',
    'version': 'some number',
    'roots':
    {
        'synced': {JSON object describing stuff synced with mobile devices using Chrome},
        'sync_transaction_version': 'some number',
        'bookmark_bar': {JSON object encapsulating the whole directory structure of bookmarks},
        'other': {JSON object like for 'bookmark_bar', but for things in the 'Other Bookmarks'
                  folder}
    }
}
```
Note that the 'other' attribute might just be an empty object, or might not exist.

Each object that represents a directory (which supports nested directories, of course) looks like
this:
```
{
	'name': 'some_name',
	'id': 'some number',
	'type': 'folder',
	'date_added': 'some number representing the date',
	'date_modified': 'number representing the date',
	'children': [list of objects representing URLs and nested directories]
}
```
And every object that represents a URL looks like this:
```
{	
	'name': 'some name',
	'id': 'some number',
	'type': 'url',
	'date_added': 'some date number',
	'url': 'some url',
	'meta_info': {object representing some other metadata, like the date the page was last visited}
}
```
Note that 'meta_info' is optional. It might not be there.

Likewise, the format that Chrome can import is a Netscape Bookmark File (mostly HTML).
It looks like this (try exporting your bookmarks to see another example):
```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="number representing the date" LAST_MODIFIED="another date number"
    	PERSONAL_TOOLBAR_FOLDER="true">Bookmarks bar</H3>
    <DL><p>
        <DT><A HREF="some URL" ADD_DATE="date number" ICON="favicon in text form">Link 1 name</A>
        <DT><H3 ADD_DATE="date num" LAST_MODIFIED="date num">Folder 1 name</H3>
        <DL><p>
            <DT><H3 ADD_DATE="date num" LAST_MODIFIED="date num">Folder 2 name</H3>
            <DL><p>
                <DT><A HREF="some URL" ADD_DATE="date num" ICON="favicon text">Link 2 name</A>
            </DL><p>
            <DT><A HREF="some URL" ADD_DATE="date num" ICON="favicon text">Link 3 name</A>
        </DL><p>
    </DL><p>
    <DT><A HREF="some URL" ADD_DATE="date num" ICON="favicon text">Link 4 name</A>
</DL><p>
```

You might notice that the very last link is not actually contained in the bookmarks bar header. It's
actually in the 'Other Bookmarks' folder. But for whatever reason, the designers just omitted the
'Other Bookmarks' object and put all of its child objects (nested links and directories) under the
first header.

Oh, and if you're super curious what I mean by a favicon as text, here's one:
```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAB+0lEQVQ4jW2TS08bQRCEv55Zv03
wIw5LIGABdrxCNiinXJByj/JrkXyKOMApIkLiV2CkYEKIbSzvTuewDxvCrFaa2e2u7qrqkW+fvyqAqiIivLYHsnO60hjz8uNr62X
yarzJ0JInRY6iiMVigbDcrxYQkbgDVQUBBBTFGEMURTSaDY4/HRNGIf57n8HR4NUOTcaVuHIYhkz+TugFPZrNJvfje4IgYL2+zmQ
yRSTuMn2faeCco9Vq0T/q42/6PM2f6B/3abxt4CLHTnsno5gWNkDGH6C10eKgc0B1rUohXyAIAiqVCuVymXqthnMRSSgigrdqkzG
Gyx+X3I5uOflywvB0yF5nj1K5xPB0iLWWQrGAupg0kmggIqhzWGvpfuxyODhERNjv7NMLehhr6Pa61Oo1nHOIJC4gGCXuwKHkcjl
227v4vk8YhrT32vibPlEYsf1hm3wh/8wJVcWoUxTFWst0OuXi/ILZbMb11TXnZ+eEi5Crn1ecfT/j4fcD1toYRGPrPRFBVDIXNt5
tUClXGN2M2Nrewst5jMdjSsVSZncsWiJDehdSgGq1Sr6Q5+7XHcVikbU3a4zvxnFimpvMAsL/Ljw+PqJ/FM/zmM/nzG5neJ6Xig6
J/ymI9/LWWWuXAhmDMSbjmw7A6jB5iaMZ6mpA9k8U0SX/jALwDxim9Rj8lykSAAAAAElFTkSuQmCC
```

Anyway, as you might expect, this tool basically just parses a Bookmarks[.bak] file and writes a new
file with the format Chrome likes to read.

## How [do I use this]?

To convert your bookmarks file to an importable HTML file named outfile.html, do this:
```python cream.py <path-to-file-to-convert> >outfile.html```

If you want to use this tool because your bookmarks got wiped, I recommend you use the path to your
.bak file as the path argument for this script, NOT the path to the non-bak file. (Note that the
typical path to the Bookmarks.bak file looks like this:
> C:/Users/<your-name>/AppData/Local/Google/Chrome/User Data/Default/Bookmarks.bak

Once the conversion finishes, go into Chrome, start the bookmark manager, and under the 'Organize'
drop-down menu click "Import bookmarks from HTML file". Then click the new file you made.