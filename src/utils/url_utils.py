import re

import requests


def check_multiple_urls_in_text(text):
    # Define a regular expression pattern to match URLs
    url_pattern = r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)'

    # Use regex to find all URLs in the input text
    urls = list(set(re.findall(url_pattern, text)))

    # Initialize a dictionary to store the results
    url_results = {}

    for url in urls:
        # Try to make an HTTP GET request to the URL with custom headers
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                url_results[url] = True
            else:
                response_wo_last_char = requests.get(url[:-1])
                status_code_wo_last_char = response_wo_last_char.status_code
                if url[-1].isalpha() and status_code_wo_last_char == 200:
                    url_results[url[:-1]] = True
                else:
                    url_results[url] = False
        except requests.exceptions.RequestException:
            try:
                response_wo_last_char = requests.get(url[:-1])
                status_code_wo_last_char = response_wo_last_char.status_code
                if url[-1].isalpha() and status_code_wo_last_char == 200:
                    url_results[url[:-1]] = True
                else:
                    url_results[url] = False
            except requests.exceptions.RequestException:
                url_results[url] = False

    # Create a new dictionary to store non-duplicate URLs
    unique_url_results = {}

    for url in url_results.keys():
        # Check if the URL ends with a non-alphabetic character and its truncated form is in the dictionary
        if not url[-1].isalpha() and url[:-1] in url_results.keys():
            continue
        else:
            unique_url_results[url] = url_results[url]

    return unique_url_results
