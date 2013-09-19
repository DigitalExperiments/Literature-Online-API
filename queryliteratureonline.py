import re
import os
import string
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

##################
# Set Parameters #
##################

#on the following line, users should identify the site they visit in order to log in to Literature Online. The default line points users to Notre Dame's log in interface.
logintoliteratureonline = 'https://login.nd.edu/cas/login?service=https%3a%2f%2flogin.proxy.library.nd.edu%2flogin%3fqurl%3dezp.2aHR0cDovL2xpb24uY2hhZHd5Y2suY29t'

#here users should identify the path to the "texts" tab on literature online.
literatureonlinetexts = 'http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do?initialise=true'

#default value for variant spelling is off. To turn on the variant spelling option, change the following value to 1
variantspelling = 0

#default value for lemmatization is also off. To turn that feature on, change the following value to 1
lemmas = 0

#identify path to the text you would like to compare to the Literature Online database texts
pathtotarget = "C:\\Users\\Douglas\\Desktop\\QueryLiteratureOnline\\sampletarget.txt"

#create parameters for the window we'll use to slide over the target text. If targetwindowstart = 0 and targetwindowend = 3, the script will establish a sliding
#window that's three words long, and slide that window over the text (at an increment equal to the value of targetslideinterval), searching for exact matches
#and then collocate matches for each window of n words (where n = targetwindowend - targetwindowstart).

targetwindowstart = 0
targetwindowend = 3
targetslideinterval = 1
defaulttargetwindowstart = 0
defaulttargetwindowend = 3

#############################
# Define Internal Functions #
#############################

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

#compile digits and create function to determine whether string contains a digit
digitlist = re.compile('\d')

def contains_digit(d):
    return bool(digitlist.search(d))

#by default, this script will write its output to the directory in which you run the script. 
out = open("out.tsv", "w")
out.write("input file" + "\t" + "search string" + "\t" "matching text author" + "\t" + "matching text" + "\t" + "matching text publication date" + "\n")

#######################################
# Prepare to search Literature Online #
#######################################

#for a helpful introduction to the webdriver that the following lines use, see: https://selenium-python.readthedocs.org/en/latest/getting-started.html
driver = webdriver.Firefox()
driver.get(str(logintoliteratureonline))
username = driver.find_element_by_name("username")
username.send_keys("dduhaime")
password = driver.find_element_by_name("password")
password.send_keys("Nolimet@ng3r3")
password.send_keys(Keys.RETURN)

################################
# Prepare list of search terms #
################################

targettext = open(pathtotarget)
inputname = os.path.basename(pathtotarget)
readtarget = targettext.read()
targetstring = str(readtarget)
targetnoextraspaces = re.sub("\s+", " ", targetstring)
splittarget = targetnoextraspaces.split(" ")
targetwindow = splittarget[targetwindowstart:targetwindowend]
timestoloop = len(splittarget) - len(targetwindow) + 1

###############################
# Begin the exact match loops #
###############################

#each time through the loop, grab the words currently within the target window, and search for those terms on Literature Online
for looppass in range(timestoloop):
    print "started looppass"
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    exactmatchsearchterms = "'" + str(searchterms) + "'"

    #now take the search terms and query Literature Online
    driver.get(str(literatureonlinetexts))
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
    
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(exactmatchsearchterms))
    elem.send_keys(Keys.RETURN)

    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
                
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    #print splitnonstandard
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
            
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within poetry"

#now restart the loop, this time searching Literature Online's Drama holdings
    
targetwindowstart = defaulttargetwindowstart
targetwindowend = defaulttargetwindowend

for looppass in range(timestoloop):
    print "started looppass"
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    exactmatchsearchterms = "'" + str(searchterms) + "'"
    
    #now take the search terms and query Literature Online
    driver.get(str(literatureonlinetexts))
    clearsearches = driver.find_element_by_partial_link_text('TEXTS')
    clearsearches.click()
    dramaresults = driver.find_element_by_partial_link_text('Drama')
    dramaresults.click()
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
    
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(exactmatchsearchterms))
    elem.send_keys(Keys.RETURN)

    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
        
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
            
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within drama"
    
print "on to the prose"

#restart the loop again, this time searching Literature Online's Prose holdings

targetwindowstart = defaulttargetwindowstart
targetwindowend = defaulttargetwindowend

for looppass in range(timestoloop):
    print "started looppass"
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    exactmatchsearchterms = "'" + str(searchterms) + "'"
    
    #now take the search terms and query Literature Online
    driver.get("http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do")
    clearsearches = driver.find_element_by_partial_link_text('TEXTS')
    clearsearches.click()
    dramaresults = driver.find_element_by_partial_link_text('Prose')
    dramaresults.click()
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
        
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(exactmatchsearchterms))
    elem.send_keys(Keys.RETURN)
    
    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
                
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    #print splitnonstandard
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
                
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within prose"
    
#############################
# Begin the collocate loops #
#############################

targetwindowstart = defaulttargetwindowstart
targetwindowend = defaulttargetwindowend

#each time through the loop, grab the words currently within the target window, and search for those terms on Literature Online
for looppass in range(timestoloop):
    print "started looppass"
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    splitsearchterms = searchterms.split(" ")
    collocateterms = " near.3 ".join(splitsearchterms)    

    #now take the search terms and query Literature Online
    driver.get("http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do?initialise=true")
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
    
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(collocateterms))
    elem.send_keys(Keys.RETURN)

    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
                
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
            
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within poetry"

#now restart the loop, this time searching Literature Online's Drama holdings
    
targetwindowstart = defaulttargetwindowstart
targetwindowend = defaulttargetwindowend

for looppass in range(timestoloop):
    print "started looppass"
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    splitsearchterms = searchterms.split(" ")
    collocateterms = " near.3 ".join(splitsearchterms)
    
    #now take the search terms and query Literature Online
    driver.get("http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do")
    clearsearches = driver.find_element_by_partial_link_text('TEXTS')
    clearsearches.click()
    dramaresults = driver.find_element_by_partial_link_text('Drama')
    dramaresults.click()
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
    
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(collocateterms))
    elem.send_keys(Keys.RETURN)

    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
        
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
            
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within drama"
    
print "on to the prose"

#restart the loop again, this time searching Literature Online's Prose holdings

targetwindowstart = defaulttargetwindowstart
targetwindowend = defaulttargetwindowend

for looppass in range(timestoloop):
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    searchterms = " ".join(targetwindow)
    splitsearchterms = searchterms.split(" ")
    collocateterms = " near.3 ".join(splitsearchterms)
    
    #now take the search terms and query Literature Online
    driver.get("http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do")
    clearsearches = driver.find_element_by_partial_link_text('TEXTS')
    clearsearches.click()
    dramaresults = driver.find_element_by_partial_link_text('Prose')
    dramaresults.click()
    
    #if user desires variant spelling, click appropriate box
    if variantspelling == 1:
        findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
        findalternativespelling.click()
        
    #if user desires lemmas, click appropriate box
    if lemmas == 1:
        findlemmmas = driver.find_element_by_id("Lemmas")
        findlemmas.click()
        
    #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
    elem = driver.find_element_by_id("Keyword")
    elem.send_keys(str(collocateterms))
    elem.send_keys(Keys.RETURN)
    
    #instantiate another loop to run through for each page of the results--default = 1 loop through
    currentloop = 1
    desiredloopcount = 2
    
    while currentloop < desiredloopcount:
        print "started subloop"
                
        #scrape search results to find string that contains metadata of interest
        driver.implicitly_wait(20)
        html = driver.page_source
        driver.implicitly_wait(20)
        cleanhtml = removeNonAscii(html)
        soup = BeautifulSoup(cleanhtml)
        stringsoup = str(soup)
        matchstrings = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
        
        #find metadata string and mine it for relevant datafields
        for matchstring in matchstrings:
            #print matchstring
            
            #most matchstrings contain a field "author=+", but for those that do not, we use the elif and else clauses below
            if "author=" in matchstring:
                authornameplus = matchstring.split("author=")
                authorplus = authornameplus[1].split("&a")
                spacedauthortokens = authorplus[0].replace("+", " ")
                strippercents = re.sub("%..", "", spacedauthortokens)
                authordata = strippercents[:-1].lstrip().replace("Author Page", "")
            else:
                authordata = ""
            
            #get title metadata
            titlelist = re.findall(r'title[^%]+', matchstring)
            titlestring = "".join(titlelist)
            splittitlestring = titlestring.split("&")
            if splittitlestring >= 0:
                cleantexttitle = splittitlestring[0].replace("title=", "").replace("+", " ")
                texttitle = cleantexttitle.lstrip()
            else:
                texttitle = ""
            
            #get publication metadata
            publicationdateplus = matchstring.split("%28")
            if len(publicationdateplus) > 2:
                publicationdatecloser = publicationdateplus[2].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
                
            elif len(publicationdateplus) == 2:
                publicationdatecloser = publicationdateplus[1].split("%29")
                if contains_digit(publicationdatecloser[0]):
                    almostpublicationdate = publicationdatecloser[0]
                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                else:
                    publicationdate = ""
            else:
                publicationdate = ""
                
            if publicationdate == "":
                nonstandardpubdate = matchstring.split("%5B")
                if len(nonstandardpubdate) >= 2:
                    splitnonstandard = nonstandardpubdate[-1].split("%")
                    closerpublicationdate = splitnonstandard[0]
                    if contains_digit(almostpublicationdate):
                        almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                        publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                    else:
                        publicationdate = ""
            if "%" in publicationdate or len(publicationdate) < 3:
                publicationdate = ""
            else:
                publicationdate = publicationdate
                
            #write search criteria and metadata to out file
            out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(publicationdate) + "\t" + "\n")
            
        #now look to see if there are additional hits on other pages
        driver.implicitly_wait(20)
        
        try:
            findmorepages = driver.find_element_by_partial_link_text('Next')
            driver.implicitly_wait(20)
            findmorepages.click()
            currentloop += 1
            desiredloopcount += 1
        
        except NoSuchElementException:
            currentloop += 1
                        
    targetwindowstart += 1
    targetwindowend += 1
    print "moved target window within prose"
        
print "Done"