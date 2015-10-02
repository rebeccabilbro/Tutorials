# searchy.py
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
from sqlite3 import dbapi2 as sqlite


###############################################################
# Global Variables
###############################################################
stopwords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


###############################################################
# Class and Methods
###############################################################
class Crawler(object):
	'''
	Create a simple web crawler that can be seeded with a small set of pages.
	'''

	def __init__(self, dbname):
		'''
		Initialize the crawler with the name of database.
		'''
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()


	def dbcommit(self):
		self.con.commit()


	def createindextables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid, wordid, location)')
		self.con.execute('create table link(fromid integer, toid integer)')
		self.con.execute('create table linkwords(wordid, linkid)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.dbcommit()


	def gettextonly(self, soup):
		'''
		Cleans up non-text characters (e.g. tags.)
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
		Splits strings on anything that isn't a letter or a number.
		'''
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']


	def addtoindex(self, url, soup):
		'''
		Adds new words and pages to the database.
		'''
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
		'''
		Auxillary function for getting an entry id and adding
		it if it's not present.
		'''
		cur = self.con.execute("select rowid from %s where %s = '%s'" % (table, field, value))
		result = cur.fetchone()
		if result == None:
			cur = self.con.execute(
				"insert into %s (%s) values ('%s')" % (table, field, value))
			return cur.lastrowid
		else:
			return result[0]


	def addlinkref(self, urlfrom, urlto, linktext):
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
		'''
		URL is indexed if the URL has a rowid in urllist.
		'''
		result = self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
		if result != None:
			# Check if URL has been crawled
			v = self.con.execute('select * from wordlocation where urlid = %d' % result[0]).fetchone()
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
	pagelist = ['http://io9.com/']
	crawly = Crawler('searchindex.db')
	crawly.createindextables()
	crawly.crawl(pagelist, 1)
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
