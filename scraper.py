import re
from collections import Counter
import pickle
from collections import defaultdict
import lxml
from urllib.parse import *
from bs4 import BeautifulSoup

#global variables

token_count = Counter()  # (key(token), value(int))

# these need to be added to pickle later
subdomains = {}
longestPage = ""
longestPage_Size = 0
wordDict = {}   # global dictionary storing every single word and its freq

# initialize dict in case not existent
dict = {}
try:
    with open("report.pickle", "rb") as f:
        data = f.read()
        if data:
            # populate dict with previously garnered data
            dict = pickle.loads(data)
        else:
            dict = {}  # Initialize as an empty dictionary if the file is empty
except FileNotFoundError:
    dict = {}  # Initialize as an empty dictionary if the file doesn't exist #(key(url), value(list)

listOfStopwords = ["a", "able", "about", "above", "abst", "accordance", "according", "accordingly",
                   "across", "act", "actually", "added", "adj", "affected", "affecting", "affects",
                   "after", "afterwards", "again", "against", "ah", "all", "almost", "alone", "along",
                   "already", "also", "although", "always", "am", "among", "amongst", "an", "and",
                   "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything",
                   "anyway", "anyways", "anywhere", "apparently", "approximately", "are", "aren", "arent",
                   "arise", "around", "as", "aside", "ask", "asking", "at", "auth", "available", "away",
                   "awfully", "b", "back", "be", "became", "because", "become", "becomes", "becoming",
                   "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind",
                   "being", "believe", "below", "beside", "besides", "between", "beyond", "biol", "both",
                   "brief", "briefly", "but", "by", "c", "ca", "came", "can", "cannot", "can't", "cause",
                   "causes", "certain", "certainly", "co", "com", "come", "comes", "contain", "containing",
                   "contains", "could", "couldnt", "d", "date", "did", "didn't", "different", "do", "does",
                   "doesn't", "doing", "done", "don't", "down", "downwards", "due", "during", "e", "each",
                   "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "end",
                   "ending", "enough", "especially", "et", "et-al", "etc", "even", "ever", "every", "everybody",
                   "everyone", "everything", "everywhere", "ex", "except", "f", "far", "few", "ff", "fifth",
                   "first", "five", "fix", "followed", "following", "follows", "for", "former", "formerly",
                   "forth", "found", "four", "from", "further", "furthermore", "g", "gave", "get", "gets",
                   "getting", "give", "given", "gives", "giving", "go", "goes", "gone", "got", "gotten",
                   "h", "had", "happens", "hardly", "has", "hasn't", "have", "haven't", "having", "he", "hed",
                   "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "hereupon", "hers",
                   "herself", "hes", "hi", "hid", "him", "himself", "his", "hither", "home", "how", "howbeit",
                   "however", "hundred", "i", "id", "ie", "if", "i'll", "im", "immediate", "immediately",
                   "importance", "important", "in", "inc", "indeed", "index", "information", "instead",
                   "into", "invention", "inward", "is", "isn't", "it", "itd", "it'll", "its", "itself", "i've",
                   "j", "just", "k", "keep", "keeps", "kept", "kg", "km", "know", "known", "knows", "l",
                   "largely", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let",
                   "lets", "like", "liked", "likely", "line", "little", "'ll", "look", "looking", "looks",
                   "ltd", "m", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means",
                   "meantime", "meanwhile", "merely", "mg", "might", "million", "miss", "ml", "more", "moreover",
                   "most", "mostly", "mr", "mrs", "much", "mug", "must", "my", "myself", "n", "na", "name",
                   "namely", "nay", "nd", "near", "nearly", "necessarily", "necessary", "need", "needs", "neither",
                   "never", "nevertheless", "new", "next", "nine", "ninety", "no", "nobody", "non", "none",
                   "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "now", "nowhere",
                   "o", "obtain", "obtained", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "omitted",
                   "on", "once", "one", "ones", "only", "onto", "or", "ord", "other", "others", "otherwise", "ought",
                   "our", "ours", "ourselves", "out", "outside", "over", "overall", "owing", "own", "p", "page",
                   "pages",
                   "part", "particular", "particularly", "past", "per", "perhaps", "placed", "please", "plus", "poorly",
                   "possible", "possibly", "potentially", "pp", "predominantly", "present", "previously", "primarily",
                   "probably", "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite", "qv", "r", "ran",
                   "rather", "rd", "re", "readily", "really", "recent", "recently", "ref", "refs", "regarding",
                   "regardless",
                   "regards", "related", "relatively", "research", "respectively", "resulted", "resulting", "results",
                   "right",
                   "run", "s", "said", "same", "saw", "say", "saying", "says", "sec", "section", "see", "seeing",
                   "seem", "seemed", "seeming", "seems", "seen",
                   "self", "selves", "sent", "seven", "several", "shall", "she", "shed", "she'll", "shes", "should",
                   "shouldn't",
                   "show", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly",
                   "since",
                   "six", "slightly", "so", "some", "somebody", "somehow", "someone", "somethan", "something",
                   "sometime", "sometimes",
                   "somewhat", "somewhere", "soon", "sorry", "specifically", "specified", "specify", "specifying",
                   "still", "stop",
                   "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure",
                   "t", "take",
                   "taken", "taking", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that'll",
                   "thats", "that've",
                   "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby",
                   "thered", "therefore",
                   "therein", "there'll", "thereof", "therere", "theres", "thereto", "thereupon", "there've", "these",
                   "they", "theyd",
                   "they'll", "theyre", "they've", "think", "this", "those", "thou", "though", "thoughh", "thousand",
                   "throug", "through",
                   "throughout", "thru", "thus", "til", "tip", "to", "together", "too", "took", "toward", "towards",
                   "tried", "tries", "truly",
                   "try", "trying", "ts", "twice", "two", "u", "un", "under", "unfortunately", "unless", "unlike",
                   "unlikely", "until", "unto",
                   "up", "upon", "ups", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using",
                   "usually", "v", "value", "various",
                   "'ve", "very", "via", "viz", "vol", "vols", "vs", "w", "want", "wants", "was", "wasnt", "way", "we",
                   "wed", "welcome", "we'll",
                   "went", "were", "werent", "we've", "what", "whatever", "what'll", "whats", "when", "whence",
                   "whenever", "where", "whereafter",
                   "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "which", "while",
                   "whim", "whither", "who",
                   "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "whose", "why", "widely",
                   "willing", "wish", "with", "within",
                   "without", "wont", "words", "world", "would", "wouldnt", "www", "x", "y", "yes", "yet", "you",
                   "youd", "you'll", "your", "youre",
                   "yours", "yourself", "yourselves", "you've", "z", "zero"]


def scraper(url, resp):
    try:
        # Valid Statuses
        if resp.status > 199 and resp.status < 300:
            links = extract_next_links(url, resp)
            return [link for link in links if is_valid(link)]
        # Redirect Statuses
        elif resp.status > 299 and resp.status < 400:
            # Extract the redirected URL from the response headers
            redirected_url = resp.url

            if redirected_url:
                # Consider the redirected URL as valid and try to extract links
                links = extract_next_links(redirected_url, resp)
                return [link for link in links if is_valid(link)]
            else:
                links = extract_next_links(url, resp)
                return [link for link in links if is_valid(link)]
        else:
            print(f"Received Status Code {resp.status} for URL: {url}")
            return []
    except Exception as e:
        print(f"Error in scraper while processing {url}: {str(e)}")
        print(e)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    '''
    Citations: https://pythonprogramminglanguage.com/get-links-from-webpage/
    '''

    # List of hyperlinks to return
    hyperlinks = []
    unwantedTags = ["img", "nav"]  # TODO figure out any other unwanted tags
    stringWebPageContent = ""

    # checks if the response status code is 200 and the content of the page is not empty
    # if resp is not None and resp.raw_response.content:
    excludeDict = {}
    excludeDict["Problem"] = []
    try:
        soupObj = BeautifulSoup(resp.raw_response.content,
                                'lxml')  # using beautiful soup with lxml parser for better performance

        # scraping hyperlinks in webpage
        potentialHyperLinks = soupObj.find_all(
            'a')  # 'a' tag doesn't neccesarily mean hyperlink is present. must check for 'a tag with href attribute'
        for data in potentialHyperLinks:
            if data.get("href") is None:  # some hyperlinks under a-tag don't have href attribute(url)
                continue

            # check if data is a relative URL
            currentScrapedLink = data.get("href")

            # defragment split: splits current url into two, separated by the #. then takes the first half i.e. the half without the fragment
            defragmentedUrl = currentScrapedLink.split("#")[
                0]  # TODO MIGHT BE ERROR IF CURRENTSCRAPEDLINK DOES NOT ALLOW SPLIT

            # Source: https://www.webdevbydoing.com/absolute-relative-and-root-relative-file-paths/
            if defragmentedUrl:  # link exists?
                if not defragmentedUrl.startswith('http://') and not defragmentedUrl.startswith(
                        'https://'):  # absolute URL Check
                    newAbsoluteLink = urljoin(url, defragmentedUrl)
                else:
                    newAbsoluteLink = defragmentedUrl

                # http://www.ics.uci.edu/alumni/stayconnected/index.php
                parsedURL = urlparse(newAbsoluteLink)

                # http://www.ics.uci.edu/alumni/stayconnected/stayconnected/index.php
                if parsedURL.path is not None:
                    duplicate = False
                    pathDict = {}
                    urlPath = parsedURL.path.split('/')
                    for path in urlPath:
                        if path == '':
                            continue
                        if path not in pathDict:
                            pathDict[path] = 1
                        else:
                            pathDict[path] += 1

                        if pathDict[path] > 1:
                            duplicate = True
                            break

                    if duplicate:  # don't add URL to hyperlink
                        excludeDict["Problem"].append(newAbsoluteLink)
                        continue

                # Duplicate Checking
                if newAbsoluteLink in dict:
                    continue

                # at this point the link is surely valid and unique
                else:
                    listOfWords = tokenizer(soupObj.get_text("")) # fixme does this actually get all the words in a page?
                    wordCount = len(listOfWords)

                    # finally store the unique url with its word length as the value
                    dict[newAbsoluteLink] = wordCount

                    # store dict in failsafe pickle
                    with open("report.pickle", "wb") as f:
                        pickle.dump(dict, f)

                # textual check
                # if less than 10 words and no links, not valuable
                hyperlinks.append(newAbsoluteLink)

            # Citation Above. Noticed finding all a-tags doesn't provide just hyperlinks, so learned and implemented going line by line to check for href attributes
        # scraping all text in webpage for computation of number of words, common words, etc. TODO maybe just get all text from webpage

    except Exception as e:
        print("error in extract")
        print(e)
    print("***************************************************************************")
    print("EXCLUDING LIST")
    print(excludeDict["Problem"])
    return hyperlinks


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)

        # #  Check for relative URLs and convert them into absolute URLs
        # if not parsed.scheme or not parsed.netloc:
        #     absolute_url = urljoin(parent_url, url)
        #     parsed = urlparse(absolute_url)

        if parsed.scheme not in set(["http", "https"]):
            print("http or https TRAP from: ", url)
            return False

        # Check if the domain is within the allowed domains
        allowed_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu",
                           "stat.uci.edu"]  # physics.uci since using ends with allows certain domains according to log file
        tempFlag = False
        for domain in allowed_domains:
            if parsed.hostname is not None and parsed.hostname.endswith(domain):
                tempFlag = True

                ### EXTRACT SUBDOMAIN INFO ###

                subdomain = parsed.hostname.split('.')[0]  # Extract the FIRST part of the hostname which should be
                # either one of the seeds, or a novel subdomain


                seedDomain = parsed.hostname.split('.')[1]  # Extract the SECOND part of the hostname, hopefully ics

                if seedDomain == "ics": # if in ics, check if new subdomain or already known subdomain

                    if subdomain in subdomains:  # if novel subdomain but not the first, then increment
                        subdomains[subdomain] += 1
                    else:  # if first novel subdomain, then add new key to the subdomains dictionary
                        subdomains[subdomain] = 1

                ### END EXTRACT SUBDOMAIN INFO ###

                break

        if tempFlag == False:
            print("Not allowed domains Trap from: ", url)
            return False

        # # Check if the URL has a fragment identifier
        # if "#" in parsed.fragment:
        #     # Extract the URL without the fragment identifier
        #     url_without_fragment = parsed.geturl()[:parsed.geturl().rfind("#")]
        #     # Check if the URL without the fragment has been visited
        #     # url.frontier.to_be_downloaded is a list in frontier.py that stores all visited urls
        #     if url_without_fragment in dict:
        #         return False
        #         print("found fragment")
        #     else:
        #         # Mark the URL without the fragment as visited
        #         url.frontier.to_be_downloaded.add(url_without_fragment)

        # if not parsed.path.startswith("/"):
        #    return False

        blacklist = ["swiki.ics.uci.edu", "physics.uci.edu", "eecs.uci.edu", "economics.uci.edu", "linguistics.uci.edu"]
        for trap in blacklist:
            if parsed.hostname is None or parsed.hostname.endswith(trap):
                print("BLACKLISTED WEBSITE: ", url)
                return False

        # TRAP CHECKING
        # Check for common traps in the path
        path_traps = ["/calendar", "/ical", "/logout", "/search", "/error", "/login", "/auth", "/404",
                      "/~eppstein/pix/", "/~eppstein/pubs",
                      "/community/news/view_news", "/doku.php", "/ml/datasets.php", "/~agelfand", "/honors",
                      "/download.inc.php", "~dechter/r"]
        for trap in path_traps:
            if trap in parsed.path:
                print("Found trap:", trap, " in: ", url)
                return False

        # TODO check traps for tags

        # Check for common traps in the query
        query_traps = ["timestamp=", "ts=", "session=", "next_uri=", "privacy_mutation_token=", "share="]
        for trap in query_traps:
            if trap in parsed.query:
                print("Found trap:", trap, " in: ", url)
                return False

        # Check for date format traps in the path (yyyy-mm-dd format)
        # Regex searches for any parsed path that has 4, 2, and 2 digits separated by hyphens
        if re.search(r"/\d{4}-\d{2}-\d{2}/", parsed.path):
            print("Found yyyy-mm-dd trap,:", url)
            return False

        # Check for invalid file extensions
        if re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ods|mpg|img|war|apk|py|ppsx|pps)$", parsed.path.lower()):
            print("Found File Extension TRAP, ", url)
            return False
        else:
            return True

    except TypeError:
        print("error in is_valid")
        print("TypeError for ", parsed)

    return False


def tokenizer(text):  # derived from assignment 1
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return tokens


# def countWordsOnPage():  # derived from assignment 1
#     pass


def computeWordFrequencies(tokensList):  # derived from assignment 1
    token_count = defaultdict(int)
    for token in tokensList:
        token_count[token] += 1


# most common 50 words
def countCommonTokens(urlList):  # derived from assignment 1
    pass

def countUniquePages():
    print(f"Amount of unique webpages: {len(dict)}")
    return len(dict)

def getLongestPage():
    longest = 0
    for key, value in dict.items():
        if value > longest:
            longest = value
            longestPage = key
    print(f"Longest Page: {longestPage}")
    return longestPage

def countSubdomains():
    for subdomain, count in subdomains.items():
        print(f"Subdomain: {subdomain}, Count: {count}")
    return len(subdomains)

# potential universal print for all report methods. or alternatively can just have each method print by themselves at
# the end of the crawl

# def printReportInfo():
#     print("Unique Pages: ", countUniquePages(), "\n",
#             "Longest Page: ", getLongestPage(), "\n",
#             "50 Most Common Words: ", countCommonTokens(), "\n",
#             "Subdomain Frequency: ", countSubdomains(), "\n")


