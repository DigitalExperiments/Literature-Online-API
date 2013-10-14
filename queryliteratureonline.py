#!/usr/bin/env python

#import packages for the analytic routine to be performed on the user provided file
import re
import os
import string
import codecs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

#import packages for the Tkinter interface
from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image

###################################
# Create Graphical User Interface #
###################################

#create TK frame
root = Tk()
#identify the dimensions of the TK frame
root.geometry("315x305")
#title the TK frame
root.title("Literature Online API")

#create a function that will return the filepath for a file provided by the user
user_defined_filepath = {}
def selectfile():
    user_defined_filepath['filename'] = askopenfilename(filetypes=[("Text","*.txt")]) # user_defined_filepath['filename'] may now be accessed in the global scope.
   
#create variables for the checkbuttons -- default = 0, checked = 1
fuzzyspellingvariable = IntVar()
lemmatizedsearchvariable = IntVar()
exactsearchvariable = IntVar()
proximitysearchvariable = IntVar()
poetryvariable = IntVar()
dramavariable = IntVar()
prosevariable = IntVar()

#create a label for the genre selection
genrelabel = Label(root, text = "Please select desired genres:")
genrelabel.grid(row = 0, column = 0, sticky = W)

#create a series of buttons that allow users to limit search by genre
poetrybutton = Checkbutton(root, text="Poetry", variable=poetryvariable)
poetrybutton.grid(row=0, column = 1, sticky = W)

dramabutton = Checkbutton(root, text="Drama", variable=dramavariable)
dramabutton.grid(row=1, column = 0, sticky = W)

prosebutton = Checkbutton(root, text="Prose", variable=prosevariable)
prosebutton.grid(row=1, column = 1, sticky = W)

#create empty line
emptylabel = Label(root, text = "")
emptylabel.grid(row = 2, column = 0, sticky = W)

#create an entry box that allows users to specify a date range for desired matching publications
publicationdaterange = Entry(root, width = "9")
publicationdaterange.grid(row = 3, column = 1, sticky = W)
publicationdaterangelabel = Label(root, text = "Publication Date Range:")
publicationdaterangelabel.grid(row=3, column = 0, sticky = W)

#create an entry box that allows users to specify date range for author
authordaterange = Entry(root, width = "9")
authordaterange.grid(row = 4, column = 1, sticky = W)
authordaterangelabel = Label(root, text = "Author Date Range:")
authordaterangelabel.grid(row=4, column = 0, sticky = W)

#create empty line
emptylabeltwo = Label(root, text = "")
emptylabeltwo.grid(row = 5, column = 0, sticky = W)

#create a button that allows users to employ Literature Online's fuzzy spelling feature. Add the object.grid() method on new line because appending .grid() to the line in which one defines object causes Python to give the object attribute "NoneType." http://stackoverflow.com/questions/1101750/python-tkinter-attributeerror-nonetype-object-has-no-attribute-get
fuzzyspellingbutton = Checkbutton(root, text="Fuzzy Spelling", variable=fuzzyspellingvariable)
fuzzyspellingbutton.grid(row = 6, column = 0, sticky = W)

#create a button that allows users to employ Literature Online's lemmatized search feature
lemmatizedsearchbutton = Checkbutton(root, text="Lemmatize Terms", variable=lemmatizedsearchvariable)
lemmatizedsearchbutton.grid(row = 7, column = 0, sticky = W)

#create a button that allows users to submit "exact match queries"
exactmatchbutton = Checkbutton(root, text="Exact Match", variable=exactsearchvariable)
exactmatchbutton.grid(row=6, column = 1, sticky = W)

#create a button that allows users to submit "proximity queries"
proximitysearchbutton = Checkbutton(root, text="Proximity Match", variable = proximitysearchvariable)
proximitysearchbutton.grid(row=7, column = 1, sticky = W)

#create empty line
emptylabelthree = Label(root, text = "")
emptylabelthree.grid(row = 8, column = 0, sticky = W)

#create a spinbox that allows users to identify desired window length
windowlengthspinbox = Spinbox(root, from_=1, to=10, width = "9")
windowlengthspinbox.grid(row = 9, column = 1, sticky = W)
windowlengthspinboxlabel = Label(root, text = "Please select window size")
windowlengthspinboxlabel.grid(row = 9, column = 0, sticky = W)

#create a spinbox that allows users to identify desired window length
slideintervalspinbox = Spinbox(root, from_=1, to=10, width = "9")
slideintervalspinbox.grid(row = 10, column = 1, sticky = W)
slideintervalspinboxlabel =  Label(root, text = "Please select window slide interval   ")
slideintervalspinboxlabel.grid(row = 10, column = 0, sticky = W)

#create empty line
emptylabelfour = Label(root, text = "")
emptylabelfour.grid(row = 11, column = 0, sticky = W)

#create a button that allows users to find a file for analysis    
selectfilebutton = Button(root,text="Select File",command=selectfile)
selectfilebutton.grid(row = 12, column = 0, sticky = W)

##########################################
# Define Query Literature Online Process #
##########################################

#create a function that will allow the "start" button to begin further processes
def startapi(event = "<Button>"):
    print "Here we go!"
    
    #####################################
    # Establish User-Defined Parameters #
    #####################################
    
    #on the following line, users should identify the site they visit in order to log in to Literature Online. The default line points users to Notre Dame's log in interface.
    logintoliteratureonline = 'https://login.nd.edu/cas/login?service=https%3a%2f%2flogin.proxy.library.nd.edu%2flogin%3fqurl%3dezp.2aHR0cDovL2xpb24uY2hhZHd5Y2suY29t'
    
    #here users should identify the path to the "texts" tab on literature online.
    literatureonlinetexts = 'http://lion.chadwyck.com.proxy.library.nd.edu/gotoSearchTexts.do?initialise=true'
    
    #default value for variant spelling is off. To turn on the variant spelling option, change the following value to 1
    if fuzzyspellingvariable.get() == 1: 
        variantspelling = 1
    else:
        variantspelling = 0
    
    #default value for lemmatization is also off. To turn that feature on, change the following value to 1
    if lemmatizedsearchvariable.get() == 1:
        lemmas = 1
    else:
        lemmas = 0
    
    #default values for exact and proximity search will be off.
    if exactsearchvariable.get() == 1:
        exactsearchvalue = 1
    else:
        exactsearchvalue = 0
        
    if proximitysearchvariable.get() == 1:
        proximitysearchvalue = 1
    else:
        proximitysearchvalue = 0    
    
    #check value of poetry, drama, and prose variables
    if poetryvariable.get() == 1:
        poetryvalue = 1
    else:
        poetryvalue = 0
        
    if dramavariable.get() == 1:
        dramavalue = 1
    else:
        dramavalue = 0
        
    if prosevariable.get() ==1:
        prosevalue = 1
    else:
        prosevalue = 0
    
    #identify path to the text you would like to compare to the Literature Online database texts
    pathtotarget = user_defined_filepath['filename']
    
    #create binary switches for publication date range and author date range. Set default to off. If user provides these strings via the GUI, we'll change the value of these variables to 1 (or on) later in the script
    publicationdatesprovided = 0
    authordatesprovided = 0
    
    #check to see if user provided dates for publication range. If so, store those dates in memory
    if publicationdaterange.get() != "":
        publicationdatestosearch = publicationdaterange.get().split("-")
        publicationdatestosearchone = publicationdatestosearch[0]
        publicationdatestosearchtwo = publicationdatestosearch[1]
        publicationdatesprovided = 1
    else:
        pass
        
    #check to see if user provided dates for author range. If so, store those dates in memory    
    if authordaterange.get() != "":
        authordatestosearch = authordaterange.get().split("-")
        authordatestosearchone = authordatestosearch[0]
        authordatestosearchtwo = authordatestosearch[1]
        authordatesprovided = 1
    else:
        pass
    
    #create parameters for the window we'll use to slide over the target text. If targetwindowstart = 0 and targetwindowend = 3, the script will establish a sliding
    #window that's three words long, and slide that window over the text (at an increment equal to the value of targetslideinterval), searching for exact matches
    #and then collocate matches for each window of n words (where n = targetwindowend - targetwindowstart).
    targetwindowstart = 0
    targetwindowend = 0 + int(windowlengthspinbox.get())
    targetslideinterval = int(slideintervalspinbox.get())
    defaulttargetwindowstart = 0
    defaulttargetwindowend = 0 + int(windowlengthspinbox.get())
    
    #############################
    # Define Internal Functions #
    #############################
    
    def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)
    
    #compile digits and create function to determine whether string contains a digit
    digitlist = re.compile('\d')
    
    def contains_digit(d):
        return bool(digitlist.search(d))
    
    def stripTags(in_text):
            # convert in_text to a mutable object (e.g. list)
            s_list = list(in_text)
            i,j = 0,0
            while i < len(s_list):
                    # iterate until a left-angle bracket is found
                    if s_list[i] == '<':
                            while s_list[i] != '>':
                                    # pop everything from the the left-angle bracket until the right-angle bracket
                                    s_list.pop(i)	
                            # pops the right-angle bracket, too
                            s_list.pop(i)
                    else:
                            i=i+1		
            # convert the list back into text
            join_char=''
            return join_char.join(s_list)
    
    #######################
    # Prepare Output File #
    #######################
    
    #by default, this script will write its output to the directory in which you run the script. 
    out = open("lionscriptoutput.tsv", "w")
    out.write("input file" + "\t" + "search string" + "\t" "matching text author" + "\t" + "matching text" + "\t" + "matching text string" + "\t" + "matching text publication date" + "\t" + "matching text genre" + "\n")
    
    #####################
    # Fire Up Webdriver #
    #####################
    
    #for a helpful introduction to the webdriver that the following lines use, see: https://selenium-python.readthedocs.org/en/latest/getting-started.html
    driver = webdriver.Firefox()
    driver.get(str(logintoliteratureonline))
    username = driver.find_element_by_name("username")
    username.send_keys("dduhaime")
    password = driver.find_element_by_name("password")
    password.send_keys("*************")
    password.send_keys(Keys.RETURN)
    
    ################################
    # Prepare list of search terms #
    ################################
    
    #compile regex to clean input text
    re1 = re.compile( "[^a-zA-Z ]+" )
    re2 = re.compile( "  +" )
    
    targettext = open(pathtotarget)
    inputname = os.path.basename(pathtotarget)
    readtarget = targettext.read()
    targetstring = str(readtarget)
    targetasunicode = targetstring.decode("utf-8", "ignore")
    
    noperiods = targetasunicode.replace(".", "")
    nocommas = noperiods.replace(",", "")
    noexclamations = nocommas.replace("!", "")
    nocolons = noexclamations.replace(":", "")
    nosemicolons = nocolons.replace(";", "")
    nodashes = nosemicolons.replace("-", "")
    noquestions = nodashes.replace("?", "")
    noquotationmarks = noquestions.replace('"', "")
    
    targetnoextraspace = " ".join(noquotationmarks.split())
    splittarget = targetnoextraspace.split(" ")
    targetwindow = splittarget[targetwindowstart:targetwindowend]
    timestoloop = len(splittarget) - len(targetwindow) + 1
    
##############################################################################################################################################################
##### Begin the exact match loops ############################################################################################################################
##############################################################################################################################################################
    
    #first, check to make sure user wants exact matches:
    if exactsearchvalue == 1:
    
        #then, check to make sure user wants hits from poetry
        if poetryvalue == 1:
            
            #each time through the loop, grab the words currently within the target window, and search for those terms on Literature Online
            for looppass in range(timestoloop):
                targetwindow = splittarget[targetwindowstart:targetwindowend]
                searchterms = " ".join(targetwindow)
                exactmatchsearchterms = '"' + str(searchterms) + '"'
                
                #now take the search terms and query Literature Online
                driver.get(str(literatureonlinetexts))
                        
                #if user desires variant spelling, click appropriate box
                if variantspelling == 1:
                    findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
                    findalternativespelling.click()
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                    
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(exactmatchsearchterms))
                elem.send_keys(Keys.RETURN)
            
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
                
                while currentloop < desiredloopcount:
                    
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    #check to ensure that the loaded html is for hits in poetry. If this is not the case, then this particular string is not present in any
                    #poetic works on LION, so move the search window forward and restart the loop.
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        matchingtextgenre = "Poetry"
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        #if you got a drama hit, ignore those hits by restarting the poetry loop with continue method
                        currentloop += 1
                        continue
                    
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        currentloop += 1
                        continue
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                            texttitle = cleantexttitle.lstrip().rstrip()
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(searchterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
        
        #now restart the loop, this time searching Literature Online's Drama holdings
        
        #check to make sure user wants drama
        if dramavalue ==1:
            
            targetwindowstart = defaulttargetwindowstart
            targetwindowend = defaulttargetwindowend
            
            for looppass in range(timestoloop):
                targetwindow = splittarget[targetwindowstart:targetwindowend]
                searchterms = " ".join(targetwindow)
                exactmatchsearchterms = '"' + str(searchterms) + '"'
                
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
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(exactmatchsearchterms))
                elem.send_keys(Keys.RETURN)
            
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
            
                while currentloop < desiredloopcount:
                            
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    #if you get a poetry hit, ignore those hits, move search window forward, and restart the loop with continue method
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at drama, store this fact in memory
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        matchingtextgenre = "Drama"
                    
                    #elif you are looking at prose, ignore those hits, move the search window forward, and restart the loop
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        currentloop += 1
                        continue
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(searchterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
        
        #restart the loop again, this time searching Literature Online's Prose holdings
        
        #first, check to make sure user wants prose
        if prosevalue == 1:
        
            targetwindowstart = defaulttargetwindowstart
            targetwindowend = defaulttargetwindowend
            
            for looppass in range(timestoloop):
                targetwindow = splittarget[targetwindowstart:targetwindowend]
                searchterms = " ".join(targetwindow)
                exactmatchsearchterms = '"' + str(searchterms) + '"'
                
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
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                    
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(exactmatchsearchterms))
                elem.send_keys(Keys.RETURN)
                
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
            
                while currentloop < desiredloopcount:
                            
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    #if you get a poetry hit, ignore those hits, move search window forward, and restart the loop with continue method
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at drama, store this fact in memory
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at prose, ignore those hits, move the search window forward, and restart the loop
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        matchingtextgenre = "Prose"
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(searchterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(searchterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
        
##############################################################################################################################################################
##### Begin the Collocate Loops ##############################################################################################################################
##############################################################################################################################################################
    
    if proximitysearchvalue == 1:
        
        #check to see if user wants poetry
        if poetryvalue == 1:
    
            targetwindowstart = defaulttargetwindowstart
            targetwindowend = defaulttargetwindowend
            
            #each time through the loop, grab the words currently within the target window, and search for those terms on Literature Online
            for looppass in range(timestoloop):
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
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(collocateterms))
                elem.send_keys(Keys.RETURN)
            
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
            
                while currentloop < desiredloopcount:
                            
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    #check the genre of the matching results on current page
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        matchingtextgenre = "Poetry"
                    
                    #elif you are looking at drama, store this fact in memory
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at prose, ignore those hits, move the search window forward, and restart the loop
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        currentloop += 1
                        continue
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(collocateterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
        
        #now restart the loop, this time searching Literature Online's Drama holdings
        
        #first check to make sure user wants drama
        if dramavalue == 1:
            
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
                dramaresults = driver.find_element_by_partial_link_text('Drama')
                dramaresults.click()
                
                #if user desires variant spelling, click appropriate box
                if variantspelling == 1:
                    findalternativespelling = driver.find_element_by_id("SPELLING_VARIANTS")
                    findalternativespelling.click()
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(collocateterms))
                elem.send_keys(Keys.RETURN)
            
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
            
                while currentloop < desiredloopcount:
                            
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at drama, store this fact in memory
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        matchingtextgenre = "Drama"
                    
                    #elif you are looking at prose, ignore those hits, move the search window forward, and restart the loop
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        currentloop += 1
                        continue
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(collocateterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
        
        #restart the loop again, this time searching Literature Online's Prose holdings
        
        #now check to see if user wants prose
        if prosevalue == 1:
        
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
                else:
                    pass
                    
                #if user desires lemmas, click appropriate box
                if lemmas == 1:
                    findlemmas = driver.find_element_by_id("Lemmas")
                    findlemmas.click()
                else:
                    pass
                
                #if user desires to limit results to a certain publication period, populate the appropriate fields
                if publicationdatesprovided == 1:
                    providepublicationdateone = driver.find_element_by_id("PubDate1")
                    providepublicationdateone.clear()
                    providepublicationdateone.send_keys(str(publicationdatestosearchone))
                    providepublicationdatetwo = driver.find_element_by_id("PubDate2")
                    providepublicationdatetwo.clear()
                    providepublicationdatetwo.send_keys(str(publicationdatestosearchtwo))
                else:
                    pass
                
                if authordatesprovided == 1:
                    provideauthordatesone = driver.find_element_by_id("LiveDate1")
                    provideauthordatesone.clear()
                    provideauthordatesone.send_keys(str(authordatestosearchone))
                    provideauthordatestwo = driver.find_element_by_id("LiveDate2")
                    provideauthordatestwo.clear()
                    provideauthordatestwo.send_keys(str(authordatestosearchtwo))
                else:
                    pass
                    
                #the next line finds the line "<input type="text" class="input-text" name="q" id="q" />" and identify the element by its id, "q"
                elem = driver.find_element_by_id("Keyword")
                elem.send_keys(str(collocateterms))
                elem.send_keys(Keys.RETURN)
                
                #instantiate another loop to run through for each page of the results--default = 1 loop through
                currentloop = 1
                desiredloopcount = 2
            
                while currentloop < desiredloopcount:
                            
                    #reset the current link to click counter (we use this counter below, when extracting strings in context)
                    currentlinktoclick = 0
                            
                    #scrape search results to find string that contains metadata of interest
                    driver.implicitly_wait(20)
                    html = driver.page_source
                    cleanhtml = removeNonAscii(html)
                    
                    if "Texts : List of Results (Poetry)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at drama, store this fact in memory
                    elif "Texts : List of Results (Drama)" in cleanhtml:
                        currentloop += 1
                        continue
                    
                    #elif you are looking at prose, ignore those hits, move the search window forward, and restart the loop
                    elif "Texts : List of Results (Prose)" in cleanhtml:
                        matchingtextgenre = "Prose"
                        
                    htmlauthorlist = cleanhtml.split('<input type="checkbox"')
                    
                    #############################
                    # Find Metadata For Matches #
                    #############################
                        
                    #for each item in the list html author except the first item (because the first item is all that leads up to the first hit)
                    for htmlauthor in htmlauthorlist[1:]:
                        soup = BeautifulSoup(htmlauthor)
                        stringsoup = str(soup)
                        
                        matchlist = re.findall(r'\bvalue="/markedList/markedResultsItem\S*', stringsoup)
                        matchstring = "".join(matchlist)
                        
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
                                if contains_digit(closerpublicationdate):
                                    almostpublicationdate = closerpublicationdate.replace("i.e.+", "")
                                    publicationdate = re.sub('[a-zA-Z]', "", almostpublicationdate)
                                else:
                                    publicationdate = ""
                        if "%" in publicationdate or len(publicationdate) < 3:
                            publicationdate = ""
                        else:
                            publicationdate = publicationdate
                                
                        #####################################
                        # Grab Matching Strings and Context #
                        #####################################
                                
                        #check to see if there are more than eight hits in text. If there are, click the link to find all hits
                        if '<a href="/searchCom.do?' in htmlauthor:
                            
                            WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                            driver.implicitly_wait(30)
                            
                            #try to get the next hit. If you get a list index error, note that you missed one hit.
                            try:
                                driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                            
                                #add one to currentlinktoclick counter, so we won't click the same link twice
                                currentlinktoclick = currentlinktoclick + 1
                                    
                                driver.implicitly_wait(20)
                                morehitshtml = driver.page_source
                                cleanmorehitshtml = removeNonAscii(morehitshtml)
                                
                                listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                for contextstring in listofhitsincontext[1:]:
                                    splitcontextstring = contextstring.split("</dt>")
                                    cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                    cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                    #write search criteria and metadata to out file
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                    
                                #switch back to main page
                                driver.implicitly_wait(10)
                                driver.find_element_by_link_text('Back to results').click()
                                
                            except IndexError:
                                
                                #if you get an index error, try one more time to get the link
                                WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'View all hits in this text')))
                                driver.implicitly_wait(60)
                                
                                #second try
                                try:
                                    driver.find_elements_by_link_text('View all hits in this text')[currentlinktoclick].click()
                                    
                                    #add one to currentlinktoclick counter, so we won't click the same link twice
                                    currentlinktoclick = currentlinktoclick + 1
                                        
                                    driver.implicitly_wait(30)
                                    morehitshtml = driver.page_source
                                    cleanmorehitshtml = removeNonAscii(morehitshtml)
                                    
                                    listofhitsincontext = cleanmorehitshtml.split('<dt class="textDT">...')
                                    for contextstring in listofhitsincontext[1:]:
                                        splitcontextstring = contextstring.split("</dt>")
                                        cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                        cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                        #write search criteria and metadata to out file
                                        out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                        
                                    #switch back to main page
                                    driver.implicitly_wait(10)
                                    driver.find_element_by_link_text('Back to results').click()
                                      
                                except IndexError:
                                    out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + "COULD NOT RETRIEVE ADDITIONAL MATCHING STRINGS WITHIN THIS TEXT CONTAINING THE SEARCH TERMS: " + str(collocateterms)  + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                   
                        else:
                            listofhitsincontext = htmlauthor.split('<dt class="textDT">...')
                            for contextstring in listofhitsincontext[1:]:
                                splitcontextstring = contextstring.split("</dt>")
                                cleancontextstring = "..." + str(stripTags(splitcontextstring[0]))
                                cleanercontextstring = cleancontextstring.replace("&amp;c.", "&c.")
                                #write search criteria and metadata to out file
                                out.write(str(inputname) + "\t" + str(collocateterms) + "\t" + str(authordata) + "\t" + str(texttitle) + "\t" + str(cleanercontextstring) + "\t" + str(publicationdate) + "\t" + str(matchingtextgenre) + "\t" + "\n")
                                
                    #now wait a moment and then look to see if there are additional hits on other pages
                    driver.implicitly_wait(10)
                    
                    try:
                        findmorepages = driver.find_element_by_link_text('Next>>')
                        driver.implicitly_wait(10)
                        findmorepages.click()
                        currentloop += 1
                        desiredloopcount += 1
                    
                    except NoSuchElementException:
                        currentloop += 1
                                    
                targetwindowstart += targetslideinterval
                targetwindowend += targetslideinterval
    
    print "Done"
    driver.quit()
    root.quit()
    
###############################
# Create Start Button for GUI #
###############################

#create a start button that allows users to submit selected parameters and run the "startapi" processes
startbutton = Button(root, text="Start", command = startapi, width = 7)
startbutton.grid(row = 12, column = 1, sticky = W)
startbutton.bind("<Button>", startapi)
#startbutton.focus()

#instantiate the Tk window
root.mainloop()
