# cfc_webscraper
Web Scraper for CFC Underwriting Technical Assessment.

## Setup + Running
I developed this project in a Conda environment containing requests v2.25.1 and beautifulsoup v4.9.3 (and dependencies). A `requirements.txt` has been generated and can be used to mimic my dev environment with pip.

To run the code to demonstrate the answers to the four challenge points outlined in the document, navigate the terminal to `./src/`, and run the following in the terminal:

`$ python webscraper.py`

This will run the program, and create the two JSON output files. By default, these will be written to the top level directory of the project.
