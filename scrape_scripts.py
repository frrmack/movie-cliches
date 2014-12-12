from goose import Goose
from bs4 import BeautifulSoup
from urllib import quote
from urllib2 import urlopen
from urlparse import urljoin
import dateutil.parser
import re
import pickle
import sys


class Script(object):
    """A container to keep all scraped info about a script"""

    next_id = 0
    
    def __init__(self, title):

        self.id = Script.next_id
        Script.next_id += 1

        self.title = title
        self.url = None
        self.text_url = None
        self.text = None
        self.genres = []
        self.writers = []
        self.date = None

    def get_writers(self, soup):
        for a in soup.findAll('a', href=re.compile(r"^/writer\.php")):
            self.writers.append( a.get_text() )

    def get_genres(self, soup):
        for a in soup.findAll('a', href=re.compile(r"^/genre/")):
            self.genres.append( a.get_text() )

    def get_date(self, soup):
        date_str = soup.find(text="Script Date")
        if date_str:
            date_str = date_str.parent.next_sibling.strip(' :')
            self.date = dateutil.parser.parse(date_str)
        else:
            print >> sys.stderr, 'No date found for %s' % self.title

    def get_text_url(self, soup):
        a = soup.find('a', href=re.compile(r"^/scripts/"))
        if a:
            self.text_url = urljoin(self.url, a['href'])
        else:
            print >> sys.stderr, 'No script found for %s' % self.title

    def get_full_text(self):
        if self.text_url:
            g = Goose()
            page = g.extract(self.text_url)
            print >> sys.stderr, "Extracting text for %s" % page.title
            self.text = page.cleaned_text
        else:
            print >> sys.stderr, 'No script found for %s' % self.title
            
        




def connect(url):
    """ Connect to a url and return it's soupified version"""
    page = urlopen(url)
    soup = BeautifulSoup(page)
    return soup


def scrape_script_links(list_url):
    """ Scrape the list page for all scripts in IMSDb,
        Create a Script instance for each and record the url
        to the full text"""

    scripts = []
    soup = connect(list_url)
    h1 = soup.find(text=re.compile("All Movie Scripts on IMSDb")).parent
    for p in h1.next_siblings:
        if not p or p.name != 'p':
            continue
        link = p.a
        script = Script(link.get_text())
        script.url = urljoin(list_url, quote(link['href']))
        scripts.append(script)
    return scripts
        

def scrape_metadata(scripts):
    """ For each script, get the writers, genres, 
        date, and the url to the full text"""
    n = len(scripts)
    for i, script in enumerate(scripts):
        soup = connect(script.url)
        print >> sys.stderr, "Scraping %s (%i of %i)" % (soup.title.text, i, n)
        script.get_writers(soup)
        script.get_genres(soup)
        script.get_date(soup)
        script.get_text_url(soup)
    return scripts
        

def scrape_all_full_text(scripts):
    """Extract the full text from each script's IMSDb page"""

    n = len(scripts)
    for i, script in enumerate(scripts):
        print >> sys.stderr, '%i of %i' % (i,n)
        script.get_full_text()
    return scripts
        


if __name__ == '__main__':

    ALL_SCRIPTS_URL = "http://www.imsdb.com/all%20scripts/"

    print >> sys.stderr, "Scraping script links"
    scripts = scrape_script_links(ALL_SCRIPTS_URL)

    print >> sys.stderr, "Scraping metadata for scripts"
    scripts = scrape_metadata(scripts)

    print >> sys.stderr, "Extracting full text for each script"
    scripts = scrape_all_full_text(scripts)

    print >> sys.stderr, "Saving data to disk"
    with open("data/scripts.pkl", 'w') as datafile:
        pickle.dump(scripts, datafile)
    print >> sys.stderr, "Done."
        





