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
longestPage = ""
longestPage_Size = 0
wordDict = {}   # global dictionary storing every single word and its freq

try:
    with open("dict.pickle", "r") as f:
        dict = pickle.load(f)
except FileNotFoundError:
    dict = {}  # Initialize as an empty dictionary if the file doesn't exist #(key(url), value(list)

listOfStopwords = [  # taken from https://www.ranks.nl/stopwords, which was provided in a2 instructions
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can't", "cannot",
    "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
    "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if",
    "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
    "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]


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
                if newAbsoluteLink in dict:  # TODO FIRST SEED URL MIGHT RUN INTO DUPLICATE
                    continue
                else:
                    dict[newAbsoluteLink] = 1

                    # store in failsafe pickle
                    with open("dict.pickle", "w") as f:
                        pickle.dump(dict, f)

                # textual check goes here
                # indent correct?
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


def countWordsOnPage():  # derived from assignment 1
    pass


def computeWordFrequencies(tokensList):  # derived from assignment 1
    token_count = defaultdict(int)
    for token in tokensList:
        token_count[token] += 1


def countCommonTokens(urlList):  # derived from assignment 1
    pass

def countUniquePages():
    return len(dict)

def getLongestPage():
    longest = 0
    for key, value in dict:
        if value > longest:
            longest = value
            longestPage = key
    return longestPage

def countSubdomains():
    pass

def printReportInfo():
    println("Unique Pages: ", countUniquePages(), "\n",
            "Longest Page: ", getLongestPage(), "\n",
            "50 Most Common Words: ", countCommonTokens(urlList), "\n",
            "Subdomain Frequency: ", countSubdomains(), "\n")


