# This Python file uses the following encoding: utf-8
# encoding: utf-8



#########################
#### Please Read!!! #####
# German parsing uses textblob:   https://pypi.python.org/pypi/textblob-de/
# This package requires NLTK >=3.1, which might not be compatible with old code!
# pip install -U textblob-de
# python -m textblob.download_corpora

from bs4 import BeautifulSoup
from textblob_de import TextBlobDE as TextBlob
import requests
import codecs
import json
from Article import Article

URLhead = "http://www.nachrichtenleicht.de/"

ArchiveList_URLheads = ["http://www.nachrichtenleicht.de/nachrichten.2005.de.html?drbm:page=",
                        "http://www.nachrichtenleicht.de/kultur.2006.de.html?drbm:page=",
                        "http://www.nachrichtenleicht.de/vermischtes.2007.de.html?drbm:page=",
                        "http://www.nachrichtenleicht.de/sport.2004.de.html?drbm:page="]
doc_ids = []

Total_Article_Num = 4 * 10 * 5

def read_text_from_web():

    #########TODO Read Exisiting File

    print "Reading Texts from www.nachrichtenleicht.de ..."

    f = codecs.open('Text/nachrichtenleicht.txt', 'w', 'utf-8')

    for url_heads in ArchiveList_URLheads:
        for page_num in range(1,1 + Total_Article_Num/4/10):  # 10 articles per page
            soup = BeautifulSoup(requests.get(url_heads + str(page_num)).text, "lxml")
            for article in soup.find_all('article', class_='dra-lsp-element'):
                a = article.find('a', text='Weiterlesen')
                #for a in article.find_all('a', text='Weiterlesen'):
                doc_ids.append(a.get('href'))

    print "Read", Total_Article_Num, "document ids complete."

    for i in range(len(doc_ids)):
        doc_id = doc_ids[i]
        soup = BeautifulSoup(requests.get(URLhead + doc_id).text, "lxml")
        title = soup.find('div', class_="dra-lsp-artikel-haupttext-headline").find('a').text
        paras = [para.text.strip() for para in soup.find('div', class_="dra-lsp-artikel-haupttext-absatz rte").find_all('p')]
        paras = [p for p in paras if len(p) > 0]
        f.write(doc_id + '\n' + title + '\n' + '\n'.join(paras) + '\n\n')
        if (i+1)%10 == 0:
            print i+1,'/', Total_Article_Num

    f.close()

    print "Reading text from web complete."
    print


def convert_text_to_articles(fn='Text/nachrichtenleicht.txt', if_article=True, if_para=True, if_twinsentence=True, if_sentence=True):
    print "Converting nachrichtenleicht.de text to Article ..."
    fi = codecs.open(fn, "r", "utf-8")
    fo = codecs.open('Text/nachrichtenleicht_articles.txt','w','utf-8')
    status = 0
    sentence_article = []
    para_article = []
    cnt = 0
    for line in fi:
        if status == 0:
            doc_id = line[:-1]
            status = 1
        elif status == 1:
            title = line[:-1]
            status = 2
        elif len(line) > 1:
            para_text = line[:-1]
            blob = TextBlob(para_text)
            for sentence in blob.sentences:
                id = doc_id + "_para" + str(len(para_article) + 1) + "_s" + str(len(sentence_article) + 1)
                text = str(sentence)
                wl = list(sentence.words.lemmatize())
                wl = [w for w in wl if not w[0] in [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']]
                uniq_wl = list(set(wl))
                sentence_article.append(Article(id, text, wl, uniq_wl))

            if if_sentence and len(sentence_article) > 1:
                for article in sentence_article:
                    fo.write(json.dumps(article.__dict__) + "\n")

            if if_twinsentence and len(sentence_article) > 2:
                for i in range(len(sentence_article)-1):
                    id = doc_id + "_para" + str(len(para_article) + 1) + "_ts" + str(i + 1)
                    text = sentence_article[i].text + ' ' + sentence_article[i+1].text
                    wl = sentence_article[i].wordlist + sentence_article[i+1].wordlist
                    uniq_wl = list(set(wl))
                    article = Article(id, text, wl, uniq_wl)
                    fo.write(json.dumps(article.__dict__) + "\n")

            id = doc_id + "_para" + str(len(para_article) + 1)
            text = ' '.join([a.text for a in sentence_article])
            wl = []
            for a in sentence_article:
                wl = wl + a.wordlist
            uniq_wl = list(set(wl))
            para_article.append(Article(id, text, wl, uniq_wl))
            sentence_article = []

        else:           #Blank Line, End of Document
            if if_para and len(para_article) > 1:
                for article in para_article:
                    fo.write(json.dumps(article.__dict__) + "\n")

            status = 0
            id = doc_id
            text = '\n'.join([a.text for a in para_article])
            wl = []
            for a in para_article:
                wl = wl + a.wordlist
            uniq_wl = list(set(wl))
            article = Article(id, text, wl, uniq_wl)
            if if_article:
                fo.write(json.dumps(article.__dict__) + "\n")
            para_article = []
            cnt += 1
            if cnt % 10 == 0:
                print cnt, "/", Total_Article_Num


    fi.close()
    fo.close()
    print "Converting text to Article complete."
    print


def read_article_list(): # Keep the order
    try:
        f = open('Text/nachrichtenleicht_articles.txt')
    except:
        return {}
    article_list = []
    for line in f:
        article_list.append(json.loads(line[:-1], object_hook=
                        lambda s:Article(s["doc_id"], s["text"], s["wordlist"], s["uniq_wordlist"])))
    return article_list

def read_articles(): # Order might be different in different OS
    article_list = read_article_list()
    articles = {a.doc_id:a for a in article_list}
    return articles



if __name__ == "__main__":
    #read_text_from_web()
    convert_text_to_articles()
