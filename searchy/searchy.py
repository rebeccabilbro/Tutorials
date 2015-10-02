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
import urllib2					# Library for downloading webpages.
from BeautifulSoup import *		# Library for parsing webpages.
from urlparse import urljoin	# Library for breaking URLs into parts.
from pysqlite2 import dbapi2 as sqlite


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
	Begin by creating a template for web crawlers that can gather
	content from the web and store it.
	'''

	def __init__(self, dbname):
		'''
		Remember that 'self' references the instance of the crawler class
		that is being initialized here. We also want to initialize the
		crawler with the name of the database. This function to tell
		'self' how to connect to the database using SQLite.
		'''
		pass # fill this in

	def __del__(self):
		'''
		This special method should allow us to disconnect from the database.
		'''
		pass # fill this in

	def dbcommit(self):
		'''
		This method should let us commit to the database.
		'''
  		pass # fill this in


	def createindextables(self):
		'''
		Ok, here's the meat of this workshop.
		We're going to need to add a bunch of different tables
		to our database so that our information is organized.

		Take a close look at 'schema.png'.

		Create five tables as follows:
		1. a table to hold all the URLs we've indexed
		2. a table to hold all the words
		3. a table to hold the locations of words within the webpages
		4. a table to hold the words actually used in links
		5. a table to hold the relationships between linked pages

		We also need to connect the tables together - but I did
		that part for you below.
		'''
		# finish filling this in by adding the 5 tables to the database
		#
		#
		#
		#
		#
		self.con.execute('create index word_idx on wordlist(word)')
		self.con.execute('create index url_idx on urllist(url)')
		self.con.execute('create index wordurl_idx on wordlocation(word_id)')
		self.con.execute('create index urlto_idx on link(to_id)')
		self.con.execute('create index urlfrom_idx on link(from_id)')
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
			result_text = ''
			for text_node in c:
				subtext = self.get_text_only(text_node)
				result_text += subtext + '\n'
					return result_text
		else:
			return v.strip()


	def separatewords(self, text):
		'''
		We also want to be able to split our strings of text into
		separate words. For now, let's assume that anything that isn't
		a letter or a number is a separator.

		I did this one for you. One day, you should come back to this
		function and see if you can make it better!
		'''
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']


	def addtoindex(self, url, soup):
		"""
		This method will call on the previous two methods (gettextonly
		and separatewords) to get a list of words on the page. Then it
		will add and index the page and its words to the database
		"""
		if self.is_indexed(url):
			return
		print 'Indexing ' + url

		# Get the individual words
		text = self.gettextonly(soup)
		words = self.separatewords(text)

		# Get the URL id
		url_id = self.getentryid('urllist', 'url', url)

		# Link each word to this url
		for word_loc in range(len(words)):
			word = words[word_loc]
			if word in self.stopwords:
				continue
			word_id = self.getentryid('wordlist', 'word', word)
			self.con.execute("insert into wordlocation(url_id, word_id, location) \
				values (%d, %d, %d)" % (url_id, word_id, word_loc))


	def getentryid(self, table, field, value, createnew=True):
		"""
		Auxillary function for getting an entry id and adding
		it if it's not present.
		"""
		cur = self.con.execute("select row_id from %s where %s = '%s'" % (table, field, value))
		result = cur.fetchone()
		if result == None:
			cur = self.con.execute(
				"insert into %s (%s) values ('%s')" % (table, field, value))
			return cur.lastrowid
		else:
			return result[0]


	def addlinkref(self, urlfrom, urlto, linktext):
		words = self.separatewords(linktext)
		from_id = self.getentryid('urllist','url',urlfrom)
		to_id = self.getentryid('urllist','url',urlto)
		if from_id == to_id:
			return
		cur = self.con.execute("insert into link(from_id,to_id) values (%d,%d)" % (from_id,to_id))
		link_id = cur.lastrowid
		for word in words:
			if word in stopwords:
				continue
			word_id = self.getentryid('wordlist','word',word)
			self.con.execute("insert into linkwords(link_id,word_id) values (%d,%d)" % (link_id,word_id))


	def isindexed(self, url):
		"""
		URL is indexed if the URL has a row_id in urllist.
		"""
		result = self.con.execute("select row_id from urllist where url='%s'" % url).fetchone()
		if result != None:
			# Check if URL has been crawled
			v = self.con.execute('select * from wordlocation where url_id = %d' % result[0]).fetchone()
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



if __name__ == '__main__':
    page_list = ['http://www.wikipedia.org/', 'http://www.dmoz.org/']
    c = crawler('searchindex.db')
    c.createindextables()
    c.crawl(page_list, 1)
