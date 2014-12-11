from goose import Goose
from bs4 import BeautifulSoup
from urllib import quote
from urllib2 import urlopen
from urlparse import urljoin
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
        self.text = ""
        self.url = ""


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
        
def scrape_full_text_of_scripts(scripts):
    """Extract the full text from the script's IMSDb page"""

    for script in scripts:
        g = Goose()
        page = g.extract(script.url)
        print >> sys.stderr, "Extracting %s" % page.title
        script.text = page.cleaned_text
    return scripts
        


if __name__ == '__main__':

    ALL_SCRIPTS_URL = "http://www.imsdb.com/all%20scripts/"
    print >> sys.stderr, "Scraping script links"
    scripts = scrape_script_links(ALL_SCRIPTS_URL)
    print >> sys.stderr, "Scraping full text for scripts"
    scripts = scrape_full_text_of_scripts(scripts)
    print >> sys.stderr, "Saving data to disk"
    with open("scripts.pkl", 'w') as datafile:
        pickle.dump(scripts, datafile)
    print >> sys.stderr, "Done."
        





