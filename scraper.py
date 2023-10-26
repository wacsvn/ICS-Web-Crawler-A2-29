import re
from collections import defaultdict
import lxml
from urllib.parse import urlparse
from bs4 import BeautifulSoup

#global variables
dict = {} #(key(url), value(list
listOfStopwords = [   #taken from https://www.ranks.nl/stopwords, which was provided in a2 instructions
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
        links = extract_next_links(url, resp)
        return [link for link in links if is_valid(link)]
    except Exception as e:
        print("error in scraper")
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

    defragmentedUrl = resp.url[:resp.url.rfind("#")] #derived from fragment checker in is_valid

    if defragmentedUrl in dict: #if url is already scraped, don't scrape again
        return []



    hyperlinks = []
    unwantedTags = ["img", "nav"] #TODO figure out any other unwanted tags
    stringWebPageContent = ""

    # checks if the response status code is 200 and the content of the page is not empty
    # if resp is not None and resp.raw_response.content:
    if resp is not None and resp.raw_response is not None:
        if resp.status == 200:
            try:
                soupObj = BeautifulSoup(resp.raw_response.content,'lxml')  # using beautiful soup with lxml parser for better performance

                #scraping hyperlinks in webpage
                potentialHyperLinks = soupObj.find_all('a')  # 'a' tag doesn't neccesarily mean hyperlink is present. must check for 'a tag with href attribute'
                for data in potentialHyperLinks:
                    #if data.get("href") == None: #some hyperlinks under a-tag don't have href attribute(url)
                        #continue
                    hyperlinks.append(data.get("href"))  # Citation Above. Noticed finding all a-tags doesn't provide just hyperlinks, so learned and implemented going line by line to check for href attributes

                #scraping all text in webpage for computation of number of words, common words, etc. TODO maybe just get all text from webpage
                webPageTags = soupObj.find_all()
                for tag in webPageTags:
                    if tag in unwantedTags:
                        continue
                    stringWebPageContent += tag.text.strip()


                tokensList = tokenizer(stringWebPageContent)

                while None in hyperlinks:
                    hyperlinks.remove(None)

                # return list(hyperlinks)
                return hyperlinks

            except Exception as e:
                print("error in extract")
                print(e)

    #TODO STORE IN DICTIONARY
    dict[defragmentedUrl] = 1

    # return list(hyperlinks)
    return hyperlinks


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            # print("failed at scheme")
            return False

        # Check if the domain is within the allowed domains
        allowed_domains = ["www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu"]
        if parsed.netloc not in allowed_domains:
            # print("failed at domain")
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

        #if not parsed.path.startswith("/"):
        #    return False

        # TRAP CHECKING
        # Check for common traps in the path
        path_traps = ["/calendar", "/ical", "/redirect", "/session", "/logout", "/search", "/user/", "/error",
                "/archive", "/sitemap", "/login", "/auth", "/404"]
        for trap in path_traps:
            if trap in parsed.path:
                print("Found trap:", trap)
                return False

        #TODO check traps for tags

        # Check for common traps in the query
        query_traps = ["session=", "timestamp=", "ts=", ]
        for trap in query_traps:
            if trap in parsed.query:
                print("Found trap:", trap)
                return False

        # Check for date format traps in the path (yyyy-mm-dd format)
        # Regex searches for any parsed path that has 4, 2, and 2 digits separated by hyphens
        if re.search(r"/\d{4}-\d{2}-\d{2}/", parsed.path):
            print("Found yyyy-mm-dd trap")
            return False

        # Check for invalid file extensions
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("error in is_valid")
        print ("TypeError for ", parsed)


    #return True



def tokenizer(text): #derived from assignment 1
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return tokens

def countWordsOnPage(): #derived from assignment 1
    pass

def computeWordFrequencies(tokensList): #derived from assignment 1
    token_count = defaultdict(int)
    for token in tokensList:
        token_count[token] += 1

def countCommonTokens(urlList): #derived from assignment 1
    pass



# Testing:
url = "http://www.ics.uci.edu/calendar/"
if is_valid(url):
    print("This URL is valid.")
else:
    print("This URL is not valid.")


