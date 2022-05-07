from duckduckgo_search import ddg

def ddg_search(query_words):
    keywords = query_words
    results = ddg(keywords, region='wt-wt', safesearch='Moderate', time='y', max_results=3)
    modified_results = []
    for i in range(0,len(results)):
        d = {}
        d['title'] = results[i]['title']
        d['url'] = results[i]['href']
        modified_results.append(d)

    return modified_results
