import glob
import os
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup as bs
from pandas import DataFrame


def get_free_proxies(url_proxy):
    proxies = []
    for url in url_proxy:
        # get the HTTP response and construct soup object
        soup = bs(requests.get(url).content, "html.parser")
        for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
            tds = row.find_all("td")
            try:
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                host = f"{ip}:{port}"
                proxies.append(host)
                print(host)
            except IndexError:
                continue
    return proxies


def get_session(proxies):
    # construct an HTTP session
    session = requests.Session()
    # choose one random proxy
    proxy = proxies.pop()
    print("proxy : " + proxy)
    session.proxies = {"http": proxy, "https": proxy}
    return session


def get_comment(comment_list, session_proxy, page_post_id, token, count_request):
    url = 'https://graph.facebook.com/' + str(page_post_id) + '?access_token=' + token + '&pretty=1&limit=100'
    err = 0
    comment_list_temp = []
    try:
        check = 0
        while True:
            id_ = session_proxy.get(url, timeout=4)
            count_request += 1
            if check == 0:
                check = 1
                if 'comments' in json.loads(id_.content):
                    for i in json.loads(id_.content)["comments"]["data"]:
                        text = i['message'].replace("\n", " ")
                        if len(text) > 0:
                            print(text)
                            message = {"review_text": text, "lable": -1}
                            comment_list.append(message)
                            comment_list_temp.append(text)
                    if 'next' in json.loads(id_.content)["comments"]['paging']:
                        url = json.loads(id_.content)["comments"]['paging']['next']
                    else:
                        break
                else:
                    break
            elif check == 1:
                if len(json.loads(id_.content)["data"]) > 0:
                    for i in json.loads(id_.content)["data"]:
                        text = i['message'].replace("\n", " ")
                        if len(text) > 0:
                            print(text)
                            message = {"review_text": text, "lable": -1}
                            comment_list.append(message)
                    if 'next' in json.loads(id_.content)['paging']:
                        url = json.loads(id_.content)['paging']['next']
                    else:
                        break
                else:
                    break

    except:
        err = 1
    return comment_list, err, count_request, comment_list_temp


def getcomments(comment_list, session_proxy, token, csv_list_idpost, count_request):
    while len(csv_list_idpost) > 0:
        post_df = csv_list_idpost[0]

        print('***************' + str(post_df) + '***************')
        print('---------------------' + str(count_request) + '------------------------')

        comment_, err, count_request, comment_list_temp = get_comment(comment_list, session_proxy, str(post_df), token,
                                                                      count_request)

        if len(comment_list_temp) >= 0 and err == 0:
            csv_list_idpost.remove(csv_list_idpost[0])

        if err == 1:
            break
        if count_request + 10 > 600:
            break


def main_getcomments(token):
    list_url_proxy = ["https://free-proxy-list.net/", "https://www.sslproxies.org/"]
    proxies = get_free_proxies(list_url_proxy)

    csv_list_idpost = glob.glob("postid_files/*.csv")
    for f in csv_list_idpost:

        page = os.path.splitext(os.path.split(f)[1])[0]
        # read posts data from csv file
        post_df = pd.read_csv(f, encoding='utf-8-sig')["Post_Id"]
        post_list = post_df.values.tolist()

        comment_list = []
        for i in range(len(proxies)):
            try:
                count_request = 0
                s = get_session(proxies)
                getcomments(comment_list, s, token, post_list, count_request)
            except Exception as e:
                continue
        path = 'comment_files/'
        if not os.path.isdir(path):
            os.mkdir(path)
        df = DataFrame(comment_list, columns=['review_text', 'lable'])
        export_csv = df.to_csv(path + page + '_comments.csv', index=None, header=True)


def get_idpost_Tu_support(token):
    with open('page_list/idfanpagelist.txt') as f:
        page_list = f.readlines()
        f.close()
    page_list = [i.strip() for i in page_list]

    for idpage in page_list:
        id_feed = 'https://graph.facebook.com/v10.0/' + idpage + '/feed?access_token=' + token + '&limit=100&after='
        id_feeds = []
        check_break = 0
        while True:
            if check_break == 5:
                break
            id_fe = requests.get(id_feed)
            if 'error' in json.loads(id_fe.content):
                check_break += 1
                continue
            else:
                if len(json.loads(id_fe.content)['data']) > 0:
                    for i in json.loads(id_fe.content)['data']:
                        id_feeds.append(i['id'])
                        print(i['id'])
                    id_feed = json.loads(id_fe.content)['paging']['next']
                else:
                    break

        feed_df = pd.DataFrame({'Post_Id': id_feeds})

        path = 'postid_files/'
        if not os.path.isdir(path):
            os.mkdir(path)

        feed_df.to_csv(path + str(idpage) + '_postid.csv')
        print('Done! Collected ', len(feed_df), ' posts from ' + str(idpage))


def main(token, get_IDpost=False, getComments=False):
    if get_IDpost:
        get_idpost_Tu_support(token)
    if getComments:
        main_getcomments(token)


if __name__ == '__main__':
    list_token = []
    token = "EAAAAZAw4FxQIBALx8TtjkfXkwppY7fhlyV1pDFY3dtQGZCo3Au8BQFVSIDS1VR0pZBKQr03jUqOPM8ljkCr4BWErRskbHbCCHCr79sHKhjCtvR0Qqe3VVZCqcCCs4uz3ECZAKq4JrNxbeDjuE6lNygmRL9qf5ZBHp7nA4KR3C2tQZDZD"
    list_token.append(token)
    main(token, get_IDpost=False, getComments=True)
