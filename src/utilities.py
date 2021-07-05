import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import json
import string


# Export a 'item' to json file at the given 'file_loc'
#   'file_loc' - string, location (including file name) to save the file
#   'item' - obj, the object to be jsonified and written to a file
def export_to_json(file, item):
    with open(file, 'w') as f:
        json.dump(item, f, indent=4)
    print(f"File saved to '{file}'")


# Determines if a location is external, based on the given index address and
#   the given location
#   'location' - string, a resource URL which is being evaluated
def location_is_external(location):
    # Prevent empty string
    if (not location):
        return False

    # Local files, denoted by local reference '/' are considered not external, as are
    #       fragment links '#' 
    # ? (fragments wont link to resources, but this may have other use cases if extended)
    if (location[0] == '/' or location[0] == '#'):
        return False

    return True


# From the BeautifulSoup of a page, and a given tag and respective attribute, return a
#   a list of all 'attribute' attributes for each 'tag' Element.
#   'soup: the BeautifulSoup object of the page
#   'tag': string, name of the tag we want to filter by
#   'attribute': string, name of the attribute for the tag which links to a resource
def get_attributes_for_tag(soup, tag, attribute):
    ls = []

    for item in soup.findAll(tag):
        try: 
            location = item[attribute]
            ls.append(location)
        except KeyError:
            # Item doesnt have the desired attribute
            pass

    return ls


# Identify external links/URLs from the BeautifulSoup of a page. This is done by
#   calling 'get_external_resources_for_tag' for different types of tags which can
#   access external resources - potentially using different attribute names.
#   'url': string, the URL of the target page to get the list of resources from.
# ? Could be extended to include new tag types - this only covers what tags were present on examination
def get_external_resources(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    resources = []
    resources.extend(get_attributes_for_tag(soup, 'img', 'src'))
    resources.extend(get_attributes_for_tag(soup, 'link', 'href'))
    resources.extend(get_attributes_for_tag(soup, 'script', 'src'))

    # Filter external_resources to remove local links and return
    external_resources = [url for url in resources if location_is_external(url)]
    return external_resources


# Creates a list of tuples in the format (URL/destination, link text) from the
#   BeautifulSoup of a page - in order to list every link on the page 
#   'url': string, url of the page with which to list its links
#   'print_links': Boolean, can be set 'True' to print each link that is examined (default 'False')
def enumerate_hyperlinks(url, print_links=False):
    # Get the page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    ls = [] 

    for link in soup.findAll('a'):
        try:
            # Get the links destination, then append to list of all links with it's text content
            link_destination = link['href']
            ls.append((link_destination, link.find(text=True)))
            if (print_links): print(link_destination)

        except KeyError:
            # No href attribute - skip invalid/non-functional hyperlink
            pass

    return ls


# From a list of (URL, link_text) tuples, attempts to identify a URL labelled/containing the text in
#   'target_text' (i.e. 'privacy policy'). Returns the URL of resource if found, else None
#   'hyperlinks': [(string, string)], a list of tuples in the form (URL, text) to be searched
#   'target_text': string, the text by which we search for the desired URL
def search_link_text(hyperlinks, target_text):
    for (hyperlink, link_text) in hyperlinks:
        try:
            if link_text.lower() == target_text.lower():
                return hyperlink
        except AttributeError:
            # link_text is NoneType (cannot perform str behaviours)
            pass
    return None


# Returns True if the content of a tag is visible on the page
#   'element': a BeautifulSoup Element which is being evaluated
#! This currently assumes that elements are not hidden by CSS
def tag_is_visible(element):
    blacklist = ['head', 'title', 'meta', 'script', 'style', '[document]']
    if element.parent.name in blacklist:
        return False
    if isinstance(element, Comment):
        return False
    return True


# Return the visible text from the soup of a page, using the filters outlines in
#   tag is visible
#   'page': Page from the result of a requests.get() operation
def visible_text_from_page(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    text = soup.findAll(text=True)
    visible_text = filter(tag_is_visible, text)
    return u' '.join(t.strip() for t in visible_text)


# Parse a page, and return a dictionary of word occurances where the keys are words,
#   and the values the respective number of occurances.
#   'link': string, the URL of the page to parse for (visible) word frequency
# ? Could add options to include hidden words in the evaluation, or blacklist certain tags etc.
def get_page_word_frequency(link):
    page = requests.get(link)

    # Get all of the page's text and clean it up
    page_text = visible_text_from_page(page)
    page_text = page_text.encode('ascii', 'ignore').decode()
    page_text = page_text.translate(str.maketrans('', '', string.punctuation))
    #! page_text = page_text.encode('ascii', 'ignore').decode()        # Remove unicode characters

    # Split the text on spaces
    page_words = page_text.split(' ')
    for word in page_words: word.strip()

    # Create a dictionary to track occurances of each word - using each word as a key
    word_occurances = {}
    for word in page_words:
        # Prevent empty string
        if (word == ''): continue

        if word.lower() in word_occurances:
            word_occurances[word.lower()] += 1
        else:
            word_occurances[word.lower()] = 1

    return word_occurances
