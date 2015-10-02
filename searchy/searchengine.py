# searchengine.py
# Georgetown University Data Science Certificate Program
# SOLUTION
# This exercise is derived from Toby Segaran's book,
# Programming Collective Intelligence (Chapter 4)


###############################################################
# Imports
###############################################################
import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import re


###############################################################
# Global Variables
###############################################################
stopwords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


###############################################################
# Class and Methods
###############################################################
class Crawler(object):
	"""
	Create a simple web crawler that can be seeded with a small set of pages.
	"""

	def __init__(self, dbname):
		"""
		Initialize the crawler with the name of database.
		"""
		self.con = sqlite.connect(dbname)


	def __del__(self):
		self.con.close()


	def dbcommit(self):
		self.con.commit()


	def createindextables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(url_id, word_id, location)')
		self.con.execute('create table link(from_id integer, to_id integer)')
		self.con.execute('create table linkwords(word_id, link_id)')
		self.con.execute('create index word_idx on wordlist(word)')
		self.con.execute('create index url_idx on urllist(url)')
		self.con.execute('create index wordurl_idx on wordlocation(word_id)')
		self.con.execute('create index urlto_idx on link(to_id)')
		self.con.execute('create index urlfrom_idx on link(from_id)')
		self.dbcommit()


	def gettextonly(self, soup):
		'''
		Cleans up non-text characters (e.g. tags.)
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
		Splits strings on anything that isn't a letter or a number.
		'''
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']


	def addtoindex(self, url, soup):
		"""
		Adds new words and pages to the database.
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
		Starting with a list of pages, do a breadth first search to the given
		depth, indexing pages as we go.
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
