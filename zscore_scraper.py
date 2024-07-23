#!/bin/python3

from bs4 import BeautifulSoup
from bs4 import element
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import statistics
from typing import List
import re

from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

from collections import defaultdict
import sys

txt_idx_by_path = defaultdict(list)
mean_by_path = dict()
txts = []
index = 0

def refuse_cookies(driver):
    try:
        time.sleep(0.5)
        driver.find_element(By.ID, "didomi-notice-agree-button").click()
    except:
        ...

already_saved_text = ""
def get_children(path_to_div, div):
# Récupérer uniquement le texte sans le contenu des balises imbriquées
    global index
    global already_saved_text
    for child in div.children:
        if isinstance(child, element.Tag):
            path_to_child = path_to_div + "/" + child.name
            """
            if child.name in ("span"):
                path_to_child = path_to_div
            else:
                path_to_child = path_to_div + "/" + child.name
            """
            if child.name in ("script", "style", "img", "span"):
                pass
            else:
                """
                content = ''.join([str(content).strip() for content in child.contents if isinstance(content, str)])
                test_is_textual = len(content) > 0
                if test_is_textual:
                """
                text = ''.join([str(content) for content in child.text if isinstance(content, str)])
                text = text.strip()
                paragraphs = re.split(r" {8,}|\n", text) # cut on newline or multiple spaces.
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    
                    if len(paragraph):
                        
                        #txt_idx_by_path[path_to_div + "/" + child.name].append(index)
                        txt_idx_by_path[path_to_child].append(index)
                        txts.append(paragraph)
                        index += 1
            #get_children(path_to_div + "/" + child.name, child)
            get_children(path_to_child, child)


def get_mean_by_category():
    """
    If multi paragraphes are far away from each other in the page, may not be the main content.
    """
    for path, indexes in txt_idx_by_path.items():
        text_lengths = [len(txts[t].replace(" ", "")) for t in indexes] # Count characters without spaces.
        mean_value = statistics.mean(text_lengths)
        mean_by_path[path] = mean_value

def get_best_candidate():
    """
    Compares the paths' results
    """
    best_path = ""
    best_mean = 0
    for path, mean in mean_by_path.items():
        if mean > best_mean:
            best_mean = mean
            best_path = path
    return best_path

def get_significant_paths_by_z_score(k=3):
    """
    Get all paths that contain more text than average.

    k: get paths with z-scores that are greater than k.
    """
    res = []
    mean_of_means = statistics.mean(mean_by_path.values())
    if len(mean_by_path) >= 2:
        std_dev_of_means = statistics.stdev(mean_by_path.values())
    else:
        std_dev_of_means = 1

    for path, mean in mean_by_path.items():
        z_score = (mean - mean_of_means) / std_dev_of_means
        if z_score >= k:
            res.append(path)
    return res

def get_significant_paths_by_clustering():
    """
    Get all paths that contain more text than average.

    k: get paths with z-scores that are greater than k.
    """

    min_mean = min(mean_by_path.values())
    max_mean = max(mean_by_path.values())

    min_cluster = dict()
    max_cluster = dict()

    for path, mean in sorted(mean_by_path.items(), key = lambda x: x[1], reverse=True):
        if abs(mean - min_mean) < abs(mean - max_mean):
            min_cluster[path] = mean
            min_mean = statistics.mean(min_cluster.values())
        else:
            max_cluster[path] = mean
            max_mean = statistics.mean(max_cluster.values())
    return max_cluster.keys()

def get_text_for_path(path: str):
    res = ""
    for txt_idx in txt_idx_by_path[path]:
        text = txts[txt_idx]
        res += text + "\n"
    return res

def get_text_for_paths(paths: List[str]):
    res = ""
    txt_idxs = set()
    for path in paths:
        for txt_idx in txt_idx_by_path[path]:
            txt_idxs.add(txt_idx)

    txt_idxs = sorted(txt_idxs)
    for txt_idx in txt_idxs:
        text = txts[txt_idx]
        if text in res:
            continue # do not add twice the same paragraph.
        res += text + "\n"
    return res

def find_title(paths: List[str]):
    pass

def find_date():
    pass

def get_one_page_content(url, method="z-score"):

    global driver
    driver.get(url)
    refuse_cookies(driver)
    time.sleep(0.2)
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    # get metadata
    title = soup.title
    if title is not None and len(title) > 0:
        title = title.get_text()
        #print("title:", title)

    publication_date = soup.find("time")
    if publication_date is not None:
        publication_date = publication_date["datetime"]
        #print("publication:", publication_date)

    body = soup.body

    get_children("", body)
    """
    for path, idxs in txt_idx_by_path.items():
        for idx in idxs:
            print(path, txts[idx])
    """

    get_mean_by_category()

    if method == "z-score":
        best_paths = get_significant_paths_by_z_score()
    elif method == "clustering":
        best_paths = get_significant_paths_by_clustering()
    if len(best_paths) > 0: # complex articles
        best_texts = get_text_for_paths(best_paths)
        #print(best_texts)
        return {"title":title, "date":publication_date, "content": best_texts}
    else: # simple articles (all text in one kind of div)
        best_path = get_best_candidate()
        best_text = get_text_for_path(best_path)
        return {"title":title, "date":publication_date, "content": best_text}
        #print(best_text)

if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]
    get_one_page_content(filename, method=method)
    driver.close()
    del(driver)
