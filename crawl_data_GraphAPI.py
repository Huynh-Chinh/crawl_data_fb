# This is a sample Python script.
import glob
import re
import os
import pandas as pd
import numpy as np
import requests
import json

def request_fanpage(page_post_id, token):
    url = 'https://graph.facebook.com/'+page_post_id+'?access_token='+token+'&limit=1000000&after=NjI2OQZDZD'
    content = requests.get(url)
    """
        created_time
        message
        actions
        comments
        from
        icon
        is_hidden
        is_expired
        link
        object_id
        picture
        privacy
        shares
        status_type
        subscribed
        type
        updated_time
        id
    """
    return content

def request_group(id_group_post, token):
    url = 'https://graph.facebook.com/'+id_group_post+'?access_token='+token+'&limit=1000000&after=NjI2OQZDZD'
    content = requests.get(url)
    """
        created_time
        message
        actions
        comments
        icon
        is_hidden
        is_expired
        link
        object_id
        picture
        privacy
        properties
        shares
        source
        status_type
        subscribed
        type
        updated_time
        id
    """
    return content

def get_content(content):
    content_post = content.json()["message"]
    return content_post

def get_comment(content):
    comment_list = []
    err = 0
    try:
        for data in content.json()["comments"]["data"]:
            text = data['message']
            text_ = text.replace("\n", " ")
            comment_list.append(text_)
    except:
        err = 1
    return comment_list, err

def get_idpost_Tu_support(token):
    with open('page_list/idfanpagelist.txt') as f:
        page_list = f.readlines()
        f.close()
    page_list = [i.strip() for i in page_list]
    print(page_list)
    for idpage in page_list:
        id_feed = 'https://graph.facebook.com/v10.0/'+idpage+'/feed?access_token=' + token + '&limit=100&after='
        id_feeds = []
        check_break = 0
        while True:
            if check_break == 10:
                break
            id_fe = requests.get(id_feed)
            # print(id_fe)
            if 'error' in json.loads(id_fe.content):
                check_break += 1
                continue
            else:
                if len(json.loads(id_fe.content)['data']) > 0:
                    for i in json.loads(id_fe.content)['data']:
                        id_feeds.append(i['id'])
                    id_feed = json.loads(id_fe.content)['paging']['next']
                else:
                    break

        feed_df = pd.DataFrame({'Post_Id': id_feeds})

        path = 'postid_files/'
        if not os.path.isdir(path):
            os.mkdir(path)

        feed_df.to_csv(path + str(idpage) + '_postid.csv')
        print('Done! Collected ', len(feed_df), ' posts from ' + str(idpage))

def getcomments(token):
    csv_list_idpost = glob.glob("postid_files/*.csv")
    for f in csv_list_idpost:
        # read posts data from csv file
        post_df = pd.read_csv(f, encoding='utf-8-sig')["Post_Id"]
        post_list = post_df.values.tolist()
        page = re.match(r"^.*\/(.*)\_.*$", f).group(1)
        comment_list = []
        id_err = []
        for post in post_list:
            print('***************' + str(post) + '***************')
            page_post_id = post
            contents = request_fanpage(page_post_id,token)
            if str(contents) == "<Response [200]>":
                comment_, err = get_comment(contents)
                if err == 0:
                    for cmt in comment_:
                        comment_list.append(cmt)
                else:
                    print('Boo!', contents)
                    id_err.append(page_post_id)
            else:
                print('Boo!', contents)
                id_err.append(page_post_id)

        with open(str(f)+"_id_err.txt", "w") as text_err:
            text_err.write(str(id_err))
            text_err.close()

        path = 'comment_files/' + page + '/'
        if not os.path.isdir(path):
            os.mkdir(path)

        label = np.negative(np.ones(len(comment_list)))
        dict = {"text":comment_list, "label":label}

        df = pd.DataFrame(dict)
        # saving the dataframe
        df.to_csv(path + f.split('_')[1].split("/")[1] +'_comments.csv')
        print('Done! Collected ', len(df), ' posts from ' + str(page))


def main(token, get_IDpost = False, getComments = False):
    if get_IDpost == True:
        get_idpost_Tu_support(token)
    if getComments == True:
        getcomments(token)


if __name__ == '__main__':
    # Use a breakpoint in the code line below to debug your script.
    token = "EAAAAZAw4FxQIBAGsZBEALWRfEtOIxv8NAokcDA0F3Nv9zsRMNTk0ZB24Tttn85xBSvEdZBE9kv8ZCWTd5DnYX458JDrOPcHpmGEhwypE1zFEP7WgfnTJhJt6ZBZBPLt5yDndrJ1oFKiK1FcQNaQZBXhHjFcZClgwhUCoKV6u6ZCTxgVgZDZD"
    main(token, get_IDpost=True, getComments=False)
