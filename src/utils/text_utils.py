import re

import bs4
import html2text
import markdown


def md_to_plaintext(md):
    html = markdown.markdown(md)
    soup = bs4.BeautifulSoup(html, features='html.parser')
    plain_text = soup.get_text()
    while "\n\n\n" in plain_text:
        plain_text = plain_text.replace("\n\n\n", "\n\n")
    return plain_text


def html_to_plaintext(html):
    converter = html2text.HTML2Text()
    plain_text = converter.handle(html)
    return plain_text


def split_string_by_regex(source_string, regex, plaintext_func=None):
    sections = re.split(regex, source_string)
    if plaintext_func:
        sections = [plaintext_func(x) for x in sections]
    sections = [x.strip() for x in sections]  # Strip
    sections = [x for x in sections if x != '']  # Remove '' paragraphs
    return sections
