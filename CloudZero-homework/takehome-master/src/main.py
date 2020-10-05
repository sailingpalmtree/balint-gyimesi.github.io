# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import asyncio
import nest_asyncio
import timeit

from absl import app
from absl import flags
from collections import Counter
from collections import defaultdict
from urllib.parse import urlparse

from typing import Dict, List


FLAGS = flags.FLAGS
HTTP_PORT = 80
HTTPS_PORT = 443

nest_asyncio.apply()

flags.DEFINE_string(
    'csv_file_path',
    ('/Users/balint/Documents/GitHub/balint-gyimesi.github.io/'
     'CloudZero-homework/top-1m.csv'),
    'Local filesystem path to a CSV file containing top sites that were opened'
    ' with a service (e.g. Alexa).')
flags.DEFINE_integer(
    'num_top_sites', 1000,
    'Number of top sites to analyze from the given zip file.', lower_bound=0)
flags.DEFINE_integer(
    'num_headers', 10,
    'Number of HTTP headers to analyze from each of the top sites.',
    lower_bound=0)


def is_url_valid(url: str) -> bool:
    """Validate that a given string is a valid URL.

    Uses a simple approach, and parses the given string with the built-in
    urlparse library. This is just a syntactical check and does not make sure
    that the given string actually points to anything.

    Todo
    ----
    Consider breaking this function out to a helpers package.

    Parameters
    ----------
    url : str
        a URL to be validated syntactically.

    Returns
    -------
    True on success, False on a syntactically invalid URL.
    """
    parse_result = urlparse(url)
    # The 'scheme' and 'netloc' fields must be populated.
    if not (parse_result.scheme and parse_result.netloc):
        print(f'The URL {url} has no valid scheme or netloc included.')
        return False
    return True


def read_csv() -> List[str]:
    """Read a given CSV file and return a list with its lines.

    The contents of the file are expected to be in this format:
        1,google.com
        2,youtube.com
        3,tmall.com
        4,baidu.com

    Todo
    ----
    Consider breaking this function out to a helpers package.

    Parameters
    ----------
    path: str
        The file system path to the csv file, containting the list of URLs.

    Returns
    -------
    csv_lines : List[str]
        The list URLs.
    """
    with open(FLAGS.csv_file_path) as csv:
        csv_lines = list()
        count = 0
        for line in csv:
            if count >= FLAGS.num_top_sites:
                break
            count += 1
            # Remove the leading number from the line, we're only interested
            # the the URL, not its rank amongst the top ones.
            csv_lines.append(line.split(',', 1)[1].strip())
        return csv_lines


def _log(msg: str) -> None:
    """Record the given message, a convenience local function.

    Todo
    ----
    - consider breaking out to helpers package.
    - use logging as well as printing, and add suport for log levels:
         import logging
         logging.log(level, msg)

    Parameters
    ----------
    msg : str
        The message to be recorded.

    """
    print(msg)


async def get_headers(url: str, all_headers: List[Dict[str, str]]) -> None:
    """Read the headers from the given url, and save them for analysis.

    Parameters
    ----------
    url : str
        A valid web URL to fetch the headers from.
    all_headers : List[Dict[str, str]]
        An existing list of which will be appended by the given url's headers.
    """
    parse_result = urlparse(url)

    if parse_result.scheme == 'https':
        reader, writer = await asyncio.open_connection(parse_result.path,
                                                       HTTP_PORT)
    else:
        reader, writer = await asyncio.open_connection(
            parse_result.path, HTTPS_PORT, ssl=True)

    # This is cribbed from Python's documentation,
    # (https://docs.python.org/3/library/asyncio-stream.html#get-http-headers)
    # but I think it could be done also with urllib and executors
    # (https://docs.python.org/3.6/library/concurrent.futures.html),
    # or even better, with grequests
    # (https://github.com/spyoungtech/grequests).
    query = (
        f"HEAD {parse_result.path or '/'} HTTP/1.0\r\n"
        f"Host: {parse_result.hostname}\r\n"
        f"\r\n"
    )

    writer.write(query.encode('latin-1'))
    headers: Dict[str, str] = dict()
    while True:
        line = await reader.readline()

        if not line:
            break

        line = line.decode('latin1').rstrip()
        if line:
            # Get the headers' names and values, by looking at what's before
            # and after the separator colon.
            elements = line.split(':', 1)
            if len(elements) == 1:
                # Headers without a value are stored with empty values.
                headers[elements[0].strip()] = ''
            else:
                headers[elements[0].strip()] = elements[1]

    # Ignore the body, close the socket
    writer.close()

    # List.append() is thread-safe.
    all_headers.append(headers)


async def get_all_headers(urls: List[str]) -> List[Dict[str, str]]:
    """Collect all headers from all the given urls.

    Parameters
    ----------
    urls : List[str]
        The list of URLs to save the HTTP/S headers from.

    Returns
    -------
    all_headers : List[Dict[str, str]]
        The list of all of the headers from all of the URLs.
    """
    all_headers: List[Dict[str, str]] = []

    # For every url, kick off an async task to fetch its headers.
    # Wait until all the headers are fetched, then return the headers.
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            asyncio.gather(*[get_headers(url, all_headers) for url in urls],
                           return_exceptions=True))
    finally:
        event_loop.close()

    return all_headers


def analyze_headers(all_headers: List[Dict[str, str]]) -> str:
    """Analyze the given list of HTTP/S headers and return the findings.

    Specifically, find:
        1 - the top 10 HTTP response headers
        2 - the percentage of sites in which each of those 10 headers appeared

    Parameters
    ----------
    all_headers: List[Dict[str, str]]
        The list of all headers for all URLs.

    Returns
    -------
    findings : str
        The result of the analysis.
    """
    # Let's count the occurrence of every individual header in every url's
    # response's headers.
    counted_headers: Dict[str, int] = defaultdict(int)
    for headers in all_headers:
        for header in headers:
            counted_headers[header] += 1

    # Figure out which are the top N individual headers.
    top_headers = Counter(counted_headers).most_common(FLAGS.num_headers)

    counter = 0
    for headers in all_headers:
        if(set(top_headers)
           .issubset(set(headers))):
            counter += 1

    percent = float(counter)/len(all_headers)
    return (
        f'The top {FLAGS.num_headers} headers are:\n{top_headers}\n\n'
        f'The percentage of sites that contain all of these top headers: '
        f'{percent:.2f}%')


async def main():
    """Run the main program."""
    # Begin measuring program runtime.
    start_timer = timeit.default_timer()

    # Read the csv file.
    sites = read_csv()

    # Get the headers from the top sites.
    headers = await get_all_headers(sites)

    # Analyze the headers.
    findings = analyze_headers(headers)
    _log(f'Analysis results: {findings}')

    #  Stop measuring program runtime, and log the result.
    stop_timer = timeit.default_timer()
    _log(f'Program runtime, in seconds: {stop_timer - start_timer}')


def absl_main(argv):
    asyncio.run(main())


if __name__ == '__main__':
    app.run(absl_main)
