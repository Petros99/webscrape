#!/usr/bin/python3
# todo
# dead link finder flag
# detect when page is taking too long to respond

# import libraries
import urllib.request  # url requesting library
import re              # regular expression library
import argparse        # argument parser library
import sys             # sys library
import urllib.parse    # url parsing library
from collections import deque  # list alternitive

# parse comand line arguments
parser = argparse.ArgumentParser()                                                       # gives the argument parser a shorter name
parser.add_argument("url", help="must be the full url eg.\"http://usd.edu\"", type=str)  # add arguments
parser.add_argument("-i", "--iterative", help="search webpages that are linked on the given one", action="store_true")
parser.add_argument("-f", help="file to send results to", type=str)
parser.add_argument("-v", help="increases verbosity", action='count')
parser.add_argument("-e", "--expression", help="the regex to use, if not specified, use one that matches email addresses", type=str)
parser.add_argument("-u", help="include the url of the page that the regex was found on", action="store_true")
parser.add_argument("-c", "--count", help="the number of pages to look through", type=int)
parser.add_argument("-b", help="--comma sepparated list of netlocs that will not be looked through", type=str)
parser.add_argument("-w", help="--comma sepparated list of netlocs that will only be looked through", type=str)
args = parser.parse_args()  # parse the arguments for use

if args.v:  # if there are more than 0 verbose flags
        def vPrint(*stuff):  # define a function to print verbosity messages, the * allows the function to accept more than one item
            print(*stuff)
else:
        def vPrint(*stuff):  # define a function that does not print verbosity messages
            None  # do nothing


def ePrint(*stuff):  # define a function to print errors
    print(*stuff, file=sys.stderr)  # print to stderr

if args.f:  # if the file option is specified
    def sendToFile(*stuff): # define a function to send data to a file
        try:
            f = open(args.f, "a")  # open the file for appending
            for thing in stuff:   # parse through all the items to send
                f.writelines(thing)  # write each item to the file
                f.writelines(' ')    # write a space char.
            f.write('\n')         # after writing all the items, add a new line
            f.close()             # and close the file
        except Exception as err:  # if some thing breaks, put the message in err
            ePrint("Failed to write to file because:", err)  # print it to stderr, but do not raise the error
else:  # if the file option was not specified
    def sendToFile(*stuff):  # create a dummy function
        None


def parseForRegex(text, compiledRegex):  # define a function
    '''checks for regex in multiline text'''
    matches = []
    for line in text:  # parse through all the lines in the text
        line = str(line)  # make sure they are strings
        match = compiledRegex.search(line)  # look for a match on the line using compiledRegex

        if match:
            matches.append(match.group(0))  # add the match to the matches list
    return matches  # return the list of matches

def hrefParser(text):  # define a function
    '''checks for href links in multiline text'''
    refs = []
    hrefExp = r"(\s)(?#matches any white space)+href=(?#matches the href= part)[\w\"-._~:/?()#@!$&\'*+,;=%\\\[\]]+(?#matches any alphanumeric and the other chars)([\s>])(?#matches any white space or the close of the tag)"
    # define the regex eg. " href=page.dfsaf(34532%232fdawefd4$#@ " would match, note the inclusion of spaces(any whitespace will work) before and after the href attrib.
    # See https://docs.python.org/3/howto/regex.html#the-backslash-plague for the reason why there is an r in front of the string
    hrefExpC = re.compile(hrefExp)  # compile the regex for faster proccessing
    for line in text:  # parse through all the lines in the text
        line = str(line)  # make sure the line is a string
        match = hrefExpC.search(line)  # find a match
        if match:
             link = match.group(0).strip().lstrip("href=").rstrip(">").strip("\"").strip("\'")  # clean up the match
             refs.append(link)  # append it to the list
    return refs # return the list

def pageDownloader(url):  # define a function to return a list of lines given a uri
    try:
        pageObj = urllib.request.urlopen(url)  # create a page object from the url
        page = pageObj.readlines()  # read all of the lines into a list
    except Exception as err:  # if something breaks, eg. a 404 error, put the error in err
        ePrint("Failed to get",url,"becuase",err)  # print message to stderr, but do not raise it
        return []  # return an empty list if error
    return page  # return the list

# handle an optional expression
if args.expression:  # if a different expression is specified on the comand line
    expression = args.expression
    expression = re.compile(expression)  #compile the expression to make it faster

else:  # if no expression is specified
    expression = re.compile('[a-zA-Z0-9]+[a-zA-Z0-9_\.-]*@[a-zA-Z0-9][a-zA-Z0-9_\.-]+(\.[a-zA-Z]{2,})')  # compile an expreson that looks for email addresses

if args.w and args.b:  # if bolth a whitelist and a blacklist are specified
    ePrint('-b and -w can not be specified together')  # print an error
    exit()  # and exit

def listCheck(netloc):  # define a function
    return False  # always be False

if args.w:  # if a whitelist is specified
    whitelist = set(args.w.split(','))  # split it up into a set

    def listCheck(netloc):  # return True for continue or False for add to todo
        if netloc in whitelist: 
            return False
        else:
            return True

if args.b: # if there is a blacklist
    blacklist = set(args.b.split(','))  # split it into a set

    def listCheck(netloc):  # return True to continue, False to add to the todo list
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
            link = deque.pop(todo)  # remove a link from todo and put it in link
        except IndexError:  # if there was an IndexError (probably because there are no more items in the deque
            print('looks like there is no more pages to proccess')
            break
        if args.count:  # if there should be a limit
            if count == args.count:  # if the limit is hit
                print("iteratitve matches:", matches)  # print matches
                break  # stop

        if link in seen:  # if the link has been seen before
            continue  # skip it
                
        page = pageDownloader(link)  # use pageDownloader to create a list of lines in the page
        for href in hrefParser(page):  # look through the page for hrefs
            (scheme, netloc, path, dumy, dumy, dumy) = urllib.parse.urlparse(href)           # split the found uri

            if listCheck(netloc):  # if listCheck says True then ignore the href
                continue

            (oldScheme, oldNetloc, oldPath, dumy, dumy, dumy) = urllib.parse.urlparse(link)  # split the current uri
            if scheme == "":  # if no scheme
                scheme = oldScheme  # use the old one
            if netloc == "":  # if no netloc
                netloc = oldNetloc  # use old one
            scheme = scheme + "://"  # fix the scheme
            oldScheme = oldScheme + "://"  # fix the old scheme
            if path == "":  # if there is no path
                path = "/"  # the path should be /

            # handle relative paths
            if path[0] == '/':  # relative to the site root
                href = scheme+netloc+path  # concatanate the uri together
            else:  # not relative to the site root
                if path[0] == '.':  # if there reference a with a dot at 0 in the path
                    ePrint("Warrning,", link , "is confusing me because of paths with a '.' in them.")  # tell the user that the script is broken and skip that one
                    continue
                else:
                    href = scheme+netloc+oldPath+"/"+path

            if href not in seen:
                todo.appendleft(href)
                vPrint(href, "found,",len(todo), "pages found so far")
                vPrint(len(seen), "pages have been proccesed")

        for rMatch in parseForRegex(page,expression):  # look through all the matches
            vPrint("found", rMatch,len(matches), "in list so far")
            matches.append(rMatch)  # add them to the list
            if args.u:  # if the user wants a url in the file with the match
                sendToFile(rMatch,link)
            else:
                sendToFile(rMatch)
        seen.add(link)
        count = count + 1
    print("iteratitve matches:", matches)

else:
    matches = parseForRegex(pageDownloader(args.url),expression)  # find matches
    print("matches:",matches)  # print them out
    for item in matches:  # send each of them to file
        sendToFile(item)
