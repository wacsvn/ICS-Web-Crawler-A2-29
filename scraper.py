import re
import lxml
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check if the domain is within the allowed domains
        allowed_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu", "today.uci.edu"]
        if parsed.netloc not in allowed_domains:
            return False

        # Check if the path (the section after the .domaintype) starts with a forward slash
        # i.e. ignore fragment URLs if that page itself has already been scraped
        # TODO this implementation doesn't account for paths that begin with / and branch into different URLS with
        #  different #'s or none at all

        # Check if the URL has a fragment identifier
        if "#" in parsed.fragment:
            # Extract the URL without the fragment identifier
            url_without_fragment = parsed.geturl()[:parsed.geturl().rfind("#")]

            # Check if the URL without the fragment has been visited
            # url.frontier.to_be_downloaded is a list in frontier.py that stores all visited urls
            if url_without_fragment in url.frontier.to_be_downloaded:
                return False
            else:
                # Mark the URL without the fragment as visited
                url.frontier.to_be_downloaded.add(url_without_fragment)

        if not parsed.path.startswith("/"):
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
        print ("TypeError for ", parsed)
        raise
