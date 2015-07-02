#!/usr/bin/python3
"""accepts a url and a regex
is able to be recursive
outputs matches to a file and stdout
"""

import urllib.request #This library allows us to retreve webpages from the internet
import re # regular expression librery

#make sure to continue on error
specialExp = re.compile('href="//[A-Za-z0-9]+.[a-z]{2,4}/?[a-zA-Z0-9$-_.+!*()?=-]*"')#must be handled first, href="//website.com"
relPageExp = re.compile('href="[$\-_.+!*()?=A-Za-z0-9]+[$\-_.+!*()/?=A-Za-z0-9]+"')#matches links that are relative to the given page
relRootExp = re.compile('href="/[$\-_.+!*()?=A-Za-z0-9]+"')#matches links that are relative to the given site
absoAddrExp = re.compile('((href="http://www.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,3}")|((href="http://www.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,3}/")|((href="http://www.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,3}/[A-Za-z0-9$-_.?+!*\(),-;\"\\\]+")')#regular expression for absolute links #href="http://www.website.com

#expression = re.compile('[a-zA-Z0-9-_\.]+@[a-zA-Z0-9-_\.]*\.[a-zA-Z]{2,4}')
emailExpression = re.compile('[a-zA-Z0-9][a-zA-Z0-9_\.-]*@[a-zA-Z0-9][a-zA-Z0-9_\.-]*\.[a-zA-Z]{2,4}')#looks for email addresses (compile makes is faster by putting it in memory)
todo = []

	#else:
		#match = linkExpresson.search(line)
		#if match:

def findPages(url):
    """
    accepts a url to search for links on 
    returns a list of links to webpages
    """
    pageObj = urllib.request.urlopen(url)
    page = pageObj.readlines()
    links = set()

    for line in page:
        line = str(line)
        matchSpecial = specialExp.search(line)
        matchRelPage = relPageExp.search(line)
        matchRelRoot = relRootExp.search(line) 
        matchAbso = absoAddrExp.search(line)

        if matchSpecial:
            links.add(str(matchSpecial.group(0)).replace('href="//','http://www.').rstrip('"'))

        elif matchAbso:
            links.add(matchAbso.group(0).replace('href="','').rstrip('"'))

        elif matchRelPage:
            links.add(matchRelPage.group(0).replace('href="',url).rstrip('"'))

        elif matchRelRoot:
            links.add(matchRelRoot.group(0).replace('href="','http://www.thesite.com').rstrip('"'))

    return links


def doPage(page):#todo is a set of pages that need to be scraped 
    """
    accepts a  pageObject to scrape
    returns a list of email addresses
    """

    rawPage = url.readlines()
    
    addresses = []
    for line in rawPage:
        line = str(line)
        match = emailExpression.search(line) #searches the line for our email address expression
        
        if match:
            addresses.append(match.group(0))

    return addresses 

url = input('What webpage do you want to look for emails on?\n')
url = urllib.request.urlopen(url)
print(doPage(url))
