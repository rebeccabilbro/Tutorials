# searchy.py
# Georgetown University Data Science Certificate Program
# WORKSHOP VERSION
# This exercise is derived from Toby Segaran's book,
# Programming Collective Intelligence (Chapter 4)

'''
Working with Databases

Have you ever wondered how a search engine works? Today
we will build one together. The basic components include:

- a way to download HTML content from the web
- a collection of webpages that you've downloaded
- a database to put that collection in (we'll use SQLite)
- a way to index the pages
- a way to parse the pages to mine for other URLs
* a way to submit a search query
* a way to return a ranked list of pages based on that query

Since the goal of this workshop is to build a functional
database, that will be the focus. For that reason, we've
left those methods in template form and have supplied other
methods for you.

We'll discuss ranking and recommender systems in more detail
in the Machine Learning and Applied Data Science courses,
For those of you who are interested in implementing a ranking
tool or recommender system in your capstone project, or if
you're curious about how the search query component works,
we highly recommend the book from which this exercise is
derived, Toby Segaran's Programming Collective Intelligence.
'''

###############################################################
# Imports
###############################################################
import urllib2            # Library for downloading webpages.
from BeautifulSoup import *    # Library for parsing webpages.
from urlparse import urljoin    # Library for breaking URLs into parts.
from sqlite3 import dbapi2 as sqlite

# Read about sqlite3 and the important commands here:
# https://docs.python.org/2/library/sqlite3.html

###############################################################
# Global Variables
###############################################################
# Do we really want our search engine to spend a lot of time on
# words that aren't very special? Nope! Let's make a variable
# here that will help our class and methods know which to ignore.
stopwords = set(['a','the','and']) #what else should we add??


###############################################################
# Class and Methods
###############################################################
class Crawler(object):
    '''
    We'll begin by creating a template for web crawlers that can
    gather content from the web and store it.
    '''

    def __init__(self, dbname):
        '''
        Remember that 'self' references the instance of the crawler class
        that is being instantiated. We also want to initialize the
        crawler with the name of the database.

        Write a method to tell 'self' how to connect to the database
        using SQLite.

        Note: you'll have to create a connection called `self.con`
        '''
        pass
        #self.con = # fill this in

    def __del__(self):
        '''
        Write a special method to allow us to disconnect from the database.
        '''
        pass # fill this in

    def dbcommit(self):
        '''
        Write a method to enable us to commit to the database.
        '''
        pass # fill this in


    def createindextables(self):
        '''
        Ok, here's the meat of this workshop.
        We're going to need to add a bunch of different tables
        to our database so that our information is organized.

        Take a close look at 'schema.png'.

        Then create five tables as follows:
        1. a table to hold all the URLs we've indexed
        2. a table to hold all the words we find
        3. a table to hold the locations of words within the webpages
        4. a table to hold the words actually used in links
        5. a table to hold the relationships between linked pages

        '''
        # Finish filling this in by adding the 5 tables to the database
        #
        #
        #
        #
        #
        # We also need to connect the tables together - but I did
        # that part for you here:
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()


    def gettextonly(self, soup):
        '''
        Since the pages you'll be scraping will have a lot of non-text
        characters (e.g. tags), let's write a method with BeautifulSoup
        to clean up.

        I did this one for you.
        '''
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ''
            for textnode in c:
                subtext = self.gettextonly(textnode)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()


    def separatewords(self, text):
        '''
        We also want to be able to split our strings of text into
        separate words. For now, let's assume that anything that isn't
        a letter or a number is a separator.

        I did this one for you, but one day, you should come back to
        this function and see if you can make it better!
        '''
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']


    def addtoindex(self, url, soup):
        """
        This method will call on the previous two methods (gettextonly
        and separatewords) to get a list of words on the page. Then it
        will add and index the page and its words to the database.

        I did this one for you.
        """
        if self.isindexed(url):
            return
        print 'Indexing ' + url

        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # Get the URL id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to this url
        for wordloc in range(len(words)):
            word = words[wordloc]
            if word in stopwords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid, wordid, location) \
                values (%d, %d, %d)" % (urlid, wordid, wordloc))


    def getentryid(self, table, field, value, createnew=True):
        """
        This is an auxillary function for getting an entry id and
        adding it to the database if it's not already there.

        I did this one for you.
        """
        cur = self.con.execute("select rowid from %s where %s = '%s'" % (table, field, value))
        result = cur.fetchone()
        if result == None:
            cur = self.con.execute(
                "insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return result[0]


    def addlinkref(self, urlfrom, urlto, linktext):
        """
        The method enables us to remember which pages linked to each other.
        This will be important for scoring and ranking later!

        I did this one for you.
        """
        words = self.separatewords(linktext)
        fromid = self.getentryid('urllist','url',urlfrom)
        toid = self.getentryid('urllist','url',urlto)
        if fromid == toid:
            return
        cur = self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid,toid))
        linkid = cur.lastrowid
        for word in words:
            if word in stopwords:
                continue
            wordid = self.getentryid('wordlist','word',word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid,wordid))


    def isindexed(self, url):
        """
        URL is indexed if the URL has a rowid in urllist.

        I did this one for you.
        """
        result = self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
        if result != None:
            # Check if URL has been crawled
            v = self.con.execute('select * from wordlocation where urlid = %d' % result[0]).fetchone()
            if v != None:
                return True
        return False


    def crawl(self,pages,depth=2):
        '''
        Finally! Here's the method that actually does the looking.
        It uses urllib2 to access webpages, BeautifulSoup to parse
        them to find any other URLs to look for, then urlparse to
        put the URLs back together.

        FYI - I filled this one in so you can focus on building the
        database!!
        '''
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                soup = BeautifulSoup(c.read())
                self.addtoindex(page,soup)

                links=soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page,link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linktext = self.gettextonly(link)
                        self.addlinkref(page,url,linktext)

                self.dbcommit()

            pages = newpages

    def geturlname(self, id):
        '''
        Once we've ranked the pages, we'll use this method to get the name
        of the top pages.
        '''
        return self.con.execute('select url from urllist where rowid=%d' % id).fetchone()[0]

    def calculatepagerank(self, iterations=20):
        '''
        This is an implementation of Google's famous PageRank algorithm.

        The algorithm calculates the probability that someone clicking around
        on the internet will end up at a certain page. The more inbound links
        the page has from other popular pages, the more likely it is that you'll
        end up there!
        '''
        # Clear out the current PageRank tables
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key, score)')

        # Initialize every URL with a PageRank 1
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()

        for i in range(iterations):
            print "Iteration %d" % (i)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr = 0.15

                # Loop through all the pages that link to this one
                for (linker,) in self.con.execute('select distinct fromid from link where toid=%d' %urlid):
                    # Get the PageRank of the linker
                    linkingpr=self.con.execute('select score from pagerank where urlid=%d' % linker).fetchone()[0]

                    # Get the total number of links from the linker
                    linkingcount = self.con.execute('select count(*) from link where fromid=%d' % linker).fetchone()[0]

                    pr += 0.85 * (linkingpr/linkingcount)
                self.con.execute('update pagerank set score=%f where urlid=%d' % (pr,urlid))
            self.dbcommit()


if __name__ == '__main__':
    pagelist = ['http://www.wikipedia.org/'] # Add your favorite webpages here!
    crawly = Crawler('searchindex.db')
    crawly.createindextables()
    crawly.crawl(pagelist, 1)

    # And now for ranking!
    crawly.calculatepagerank()
    cur = crawly.con.execute('select * from pagerank order by score desc')
    first = cur.next()
    second = cur.next()
    third = cur.next()
    winner = crawly.geturlname(first[0])
    secondplace = crawly.geturlname(second[0])
    thirdplace = crawly.geturlname(third[0])
    print 'And the winner is... %s' % winner
    print 'Second place goes to... %s' % secondplace
    print 'And the runner-up is... %s' % thirdplace
