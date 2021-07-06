import utilities 

# Set options (i.e. target webpage):
_TARGET_URL = 'https://www.cfcunderwriting.com'     # Target URL to scrape
_SAVE_DIR = '..'                                    # Target location for output files

# 1/2: Get the external resources for the target page and save the results a JSON file
external_resources = utilities.get_external_resources(_TARGET_URL)
utilities.export_to_json(f'{_SAVE_DIR}/external_resources.json', external_resources)

# 3/4: List all links on the page, parse the words on the privacy policy page:
page_hyperlinks = utilities.enumerate_hyperlinks(_TARGET_URL, print_links=False)
privacy_policy_url = utilities.search_link_text(page_hyperlinks, 'privacy policy')

# Ensure that a valid link was found, else print an error to the console
if (not privacy_policy_url):
    print("Could not find a valid link to a privacy policy!")
else:
    # If found link is with respect to TLD, append it original URL
    if (privacy_policy_url[0] == '/'): privacy_policy_url = _TARGET_URL + privacy_policy_url

    # Get the word frequency, and export it to a JSON file
    word_frequency = utilities.get_page_word_frequency(privacy_policy_url) 
    utilities.export_to_json(f'{_SAVE_DIR}/word_frequency.json', word_frequency)