import os
import shutil
import time
import requests
import json


def get_all_id_friends(id_user, token_user):
    check_break = 0
    id_friends = []
    url = 'https://graph.facebook.com/v10.0/' + id_user + '/friends?access_token=' + token_user + "&limit=100&after="
    while True:
        if check_break == 5:
            break
        id_ = requests.get(url)
        time.sleep(5)
        if 'error' in json.loads(id_.content):
            check_break += 1
        else:
            if len(json.loads(id_.content)['data']) > 0:
                for i in json.loads(id_.content)['data']:
                    id_friends.append(i['id'])
                if 'next' in json.loads(id_.content)['paging']:
                    url = json.loads(id_.content)['paging']['next']
                else:
                    break
            else:
                break

    # write list id friends of user
    text_file = open("list_id_friends.txt", "w")
    for i in id_friends:
        text_file.write(i + '\n')
    text_file.close()

    return id_friends


def get_all_profile_photos(list_id_friends, token_user):
    # Create target Directory if don't exist

    dirName = 'download_images'
    if not os.path.exists(dirName):
        os.mkdir(dirName)

    try:
        for id in list_id_friends:
            url_albums = 'https://graph.facebook.com/v10.0/' + str(id) + '/albums?access_token=' + token_user
            id_albums = requests.get(url_albums)
            time.sleep(5)
            dirName = 'download_images/' + str(id)
            if not os.path.exists(dirName):
                os.mkdir(dirName)

            for pr in json.loads(id_albums.content)['data']:
                if 'Ảnh đại diện' in pr['name'] or 'Profile pictures' in pr['name']:
                    url_p = 'https://graph.facebook.com/v10.0/' + str(
                        pr['id']) + '/photos?access_token=' + token_user + '&limit=100&fields=id,source'
                    url_photo = requests.get(url_p)
                    time.sleep(5)
                    for sr in json.loads(url_photo.content)['data']:
                        resp = requests.get(sr['source'], stream=True)
                        local_file = open('download_images/' + str(id) + '/' + str(sr['id']) + '.jpg', 'wb')
                        resp.raw.decode_content = True
                        shutil.copyfileobj(resp.raw, local_file)
                        del resp
    except:
        pass


if __name__ == "__main__":
    # token user
    token_user = "EAAAAZAw4FxQIBACkSLz75HWcQGbgnY0Nx0h1lIk6bAEKTZBJfstrPx3XZCmh5UMPgbmM6lSmgPjj3rWpOKPMR4zE6owqfZCxMkqLVqec27EUtVWwIq4T1heloiLtO5e32P0MyMUZCZAswgwkycw2GrZBS5GZARuW7HQbKqeQUgqg9QZDZD"

    # id user
    id_user = "100058787444429"

    list_id_friend = get_all_id_friends(id_user, token_user)
    get_all_profile_photos(list_id_friend, token_user)
