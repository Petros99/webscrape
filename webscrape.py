#!/usr/bin/python3
#todo
#dead link finder flag
#whitelist
#blacklist
#move away from lists
#detect when page is taking too long to respond


#import libraries
import urllib.request#url requesting library 
import re # regular expression library
import argparse #argument parser library
import sys
import urllib.parse#url parsing library
from collections import deque

#parse comand line arguments
parser = argparse.ArgumentParser()#gives the argument parser a shorter name
parser.add_argument("url", help="must be the full url eg.\"http://usd.edu\"", type=str)#adds the url argument
parser.add_argument("-i", "--iterative", help="iterative search webpages that are linked on the given one", action="store_true")#adds the -i option
parser.add_argument("-f", help="file to send results to", type=str)
parser.add_argument("-v", help="increases verbosity", action='count')
parser.add_argument("-e", "--expression", help="the regex to use when searching, if not specified the default will be used, which searches for email addresses", type=str)#adds the -e option
parser.add_argument("-u", help="include the url of the page that the regex was found on", action="store_true")
parser.add_argument("-c", "--count", help="the number of pages to look through", type=int)
parser.add_argument("-b", help="--comma sepparated list of netlocs that will not be looked through", type=str)
parser.add_argument("-w", help="--comma sepparated list of netlocs that will only be looked through", type=str)
args = parser.parse_args()#parses the arguments for use

if args.v :#if there is more than 0 verbose flags
        def vPrint(*stuff):#define a function to handle that, the * is to allow the function to accept more than one stuff
            print(*stuff)
else:#if there are 0 verbose flags
        def vPrint(*stuff):#define a function to handle that
            None#do nothing

def ePrint(*stuff):#defines a function to print errors
    print(*stuff, file=sys.stderr)

if args.f:
    def sendToFile(*stuff):
        try:
            f = open(args.f,"a")
            for thing in stuff:
                f.writelines(thing)
                f.writelines(' ')
            f.write('\n')
            f.close()
        except Exception as err:
            ePrint("Failed to write to file because:",err)
else:
    def sendToFile(*stuff):
        None


def parseForRegex(text, compiledRegex):
    '''checks for regex in multiline text'''
    matches = []
    for line in text:
        line = str(line)
        match = compiledRegex.search(line)#look for a match on the line using compiledRegex

        if match:
            matches.append(match.group(0))#add the match to the matches list
    return matches

def hrefParser(text):
    '''checks for href links in multiline text'''
    refs = []
    hrefExp = r"(\s)(?#matches any white space)+href=(?#matches the href= part)[\w\"-._~:/?()#@!$&\'*+,;=%\\\[\]]+(?#matches any alphanumeric and the other chars)([\s>])(?#matches any white space or the close of the tag)"
    #define the broadest regex eg. " href=page.dfsaf(34532%232fdawefd4$#@ " would match, note the inclusion of spaces(any whitespace will work) before and after the href attrib.
    #See https://docs.python.org/3/howto/regex.html#the-backslash-plague for the reason why there is an r in front of the string
    hrefExpC = re.compile(hrefExp)
    for line in text:
        line = str(line)
        match = hrefExpC.search(line)
        if match:
             link = match.group(0).strip().lstrip("href=").rstrip(">").strip("\"").strip("\'")
             refs.append(link)
    return refs

def pageDownloader(url):
        #if /page/doc , relative to root
        #if page/doc , relative to currnet folder
    try:
        pageObj=urllib.request.urlopen(url)
        page=pageObj.readlines()
    except Exception as err:
        ePrint("Failed to get",url,"becuase",err)
        return []
    return page #page is a list of lines

#handle an optional expression
if args.expression:#if a different expression is specified on the comand line
    expression = args.expression#put it in the var expression
    expression = re.compile(expression)#compile the expression to make it faster

else:#if no expression is specified
    expression = re.compile('[a-zA-Z0-9]+[a-zA-Z0-9_\.-]*@[a-zA-Z0-9][a-zA-Z0-9_\.-]+(\.[a-zA-Z]{2,})')#compile an expreson that looks for email addresses

if args.w and args.b:
    ePrint('-b and -w can not be specified together')

def listCheck(netloc):
    return False

if args.w:
    whitelist = set(args.w.split(','))
    def listCheck(netloc):#return True for continue or False for add to todo
        if netloc in whitelist:
            return False
        else:
            return True

if args.b:
    blacklist = set(args.b.split(','))
    def listCheck(netloc):
        if netloc in blacklist:
            return True
        else:
            return False

if args.iterative:
    todo = deque()
    todo.append(args.url)
    matches = []
    seen = set()
    count = 0
    
    while 1:
        try:
            link = deque.pop(todo)
        except IndexError as err:
            print('looks like there is no more pages to proccess')
            break
        if args.count:#if there should be a limit
            if count == args.count:#if we hit that limit
                print("iteratitve matches:",matches)#print matches
                break#stop

        if link in seen:#if we have seen the link before
            continue
                
        page = pageDownloader(link)#use pageDownloader to create a page object
        for href in hrefParser(page):#look through the page for hrefs
            (scheme, netloc, path,dumy, dumy,dumy) = urllib.parse.urlparse(href)#split the found uri
            (oldScheme, oldNetloc, oldPath,dumy, dumy,dumy) = urllib.parse.urlparse(link)#split the current uri
            if scheme == "":#if no scheme
                scheme = oldScheme#use the old one
            if netloc == "":#if no netloc
                netloc = oldNetloc#use old one
            scheme = scheme + "://"#fix the scheme
            oldScheme = oldScheme + "://"#fix the old scheme
            if path == "":#if there is no path
                path = "/"#the path should be /
            #handle relative paths

            if path[0] == '/':#relative to the site root
                href = scheme+netloc+path
            else:#not relative to the site root
                if path[0] == '.':#if there reference a with a dot at 0 in the path
                    ePrint("Warrning,", link , "is confusing me because of paths with a '.' in them.")
                    continue
                else:
                    href = scheme+netloc+oldPath+"/"+path
            if listCheck(netloc):#if listCheck says True then ignore the href
                continue

            if href not in seen:
                todo.appendleft(href)
                vPrint(href,"found,",len(todo),"pages found so far")
                vPrint(len(seen),"pages have been proccesed")
        for rMatch in parseForRegex(page,expression):#look through all the matches
            vPrint("found",rMatch,len(matches), "in list so far")
            matches.append(rMatch)#add them to the list
            if args.u:
                sendToFile(rMatch,link)
            else:
                sendToFile(rMatch)#add them to the file
        seen.add(link)
        count = count + 1
    print("iteratitve matches:",matches)

else:
    matches = parseForRegex(pageDownloader(args.url),expression)#find matches
    print("matches:",matches)#print them out
    for item in matches:#send each of them to file
        sendToFile(item)
