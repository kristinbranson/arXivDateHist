# Plot number of arXiv papers found with set queries over time.
# Based on
# arXiv_paging_example.py
# by Julius B. Lucks
# https://static.arxiv.org/static/arxiv.marxdown/0.1/help/api/examples/python_arXiv_paging_example.txt
# Modifications include modernization for Python 3 and updated urllib
# and simple histogramming of publication date.
# Kristin Branson
# kristinbranson@gmail.com
# 2022-04-07

import urllib
import time
import feedparser
import datetime
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt

"""
alldates,alltitles = \
searchpager(search_query, max_results=500000, results_per_iteration=100,
            wait_time=1, maxntries=10)
Return all arXiv papers that match the query, up to max_results papers returned. 
"""
def searchpager(search_query, max_results=500000, results_per_iteration=100,
                wait_time=1, maxntries=10):
    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    start = 0  # start at the first result

    print('Searching arXiv for %s'%search_query)
    nentries = 0
    alldates = []
    alltitles = []

    for i in range(start, max_results, results_per_iteration):

        print("Results %i - %i"%(i, i + results_per_iteration))

        query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                             i,
                                                             results_per_iteration)

        for tryn in range(maxntries):

            # perform a GET request using the base_url and query
            response = urllib.request.urlopen(base_url + query).read()

            # parse the response using feedparser
            feed = feedparser.parse(response)
            if len(feed.entries) > 0:
                break
            time.sleep(wait_time)

        # Run through each entry, and print out information
        for entry in feed.entries:
            print('arxiv-id: %s'%entry.id.split('/abs/')[-1])
            print('Title:  %s'%entry.title)
            print(f'Date: {entry.published}')
            date = datetime.datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
            alldates.append(date)
            alltitles.append(entry.title)
            # feedparser v4.1 only grabs the first author
            #print('First Author:  %s' % entry.author)

        nentries += len(feed.entries)

        if len(feed.entries) < results_per_iteration:
            break

        # Remember to play nice and sleep a bit before you call
        # the api again!
        print('Sleeping for %i seconds' % wait_time)
        time.sleep(wait_time)

    print(f'Found {nentries} entries total')
    return alldates,alltitles

def main():

    imagequery = 'abs:image+AND+abs:learning'
    imagedates,imagetitles = searchpager(imagequery)
    videoquery = 'abs:video+AND+abs:learning'
    videodates,videotitles = searchpager(videoquery)

    nbins = 50
    videodatesn = mdates.date2num(np.array(videodates))
    imagedatesn = mdates.date2num(np.array(imagedates))
    fig, ax = plt.subplots(1, 1)
    ax.hist([videodatesn,imagedatesn],nbins,density=False,label=['Video','Image'])
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%y'))
    ax.legend()
    plt.show()

if __name__ == '__main__':
    main()
