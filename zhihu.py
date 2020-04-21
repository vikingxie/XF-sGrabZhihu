# -*- coding:utf-8 -*-
import requests
import time

# headers = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
#     "Connection": "keep-alive",
#     "Host": "www.zhihu.com",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
# }

headers = {
    "Accept": "application/json, text/plain, */*",
    #"Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",
    "Connection": "keep-alive",
    "Cookie": 'aliyungf_tc=AQAAAF5MtAnG4QIAvZ6NPW2Ib/nmgYKO; d_c0="ANAseb3QAQ2PTuabHqUE4A3G2o95RYZDGQk=|1516240128"; _xsrf=b40baefa-cf71-4ba8-8d1d-c32b8b39d802; q_c1=fdb2847491d24bb48ca87ede4209d5d9|1516240128000|1516240128000',
    "Host": "www.zhihu.com",
    "origin": "https://www.zhihu.com",
    "Referer": "https://www.zhihu.com/question/31606466",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "x-udid": "ANAseb3QAQ2PTuabHqUE4A3G2o95RYZDGQk="
}

params = {
    "include": "data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics",
    "offset": "3",
    "limit": "20",
    "sort_by": "default"#created
}


def grab(url):
    res = requests.get(url, headers=headers, params=params)
    print(res.status_code)
    if res.status_code == 200:
        print(res.content)
        print(res.json()["url"])
        api_url = res.json()["url"]
        grab_answers(api_url)


def grab_answers(api_url):
    answers_url = api_url + "/answers"
    #print(answers_url)
    is_end = False
    offset = 0
    limit = 20
    of = open("of.txt", mode="w", encoding='utf-8')
    of.write('name,gender,location,employments,educations,vote up count,comment count,created time,answer\n')

    while not is_end:
        params["offset"] = offset
        params["limit"] = limit
        res = requests.get(answers_url, headers=headers, params=params)
        print('answers {0}-{1} {2}'.format(offset, offset+limit, res.status_code))
        #print(res.headers)
        if res.status_code == 200:
            #print(res.json())
            pkt = res.json()
            is_end = pkt['paging']['is_end']
            totals = pkt['paging']['totals']
            answers = pkt['data']
            for answer in answers:
                author = answer['author']
                author_name = author['name']
                author_url_token = author['url_token']
                author_location, author_employments, author_gender, author_educations = grab_author(author_url_token)

                voteup_count = answer['voteup_count']
                comment_count = answer['comment_count']
                created_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(answer['created_time']))
                answer_lines = answer['content'].splitlines()
                author_answer = ''.join(answer_lines)
                print('{0},{1},{2},{3},{4},{5},{6},{7}'.format(author_name, author_gender, author_location, author_employments, author_educations, voteup_count, comment_count, created_time))
                of.write('{0},{1},{2},{3},{4},{5},{6},{7},{8}\n'.format(author_name, author_gender, author_location, author_employments, author_educations, voteup_count, comment_count, created_time, author_answer))
                of.flush()

        offset += limit
        time.sleep(1)

    of.close()
    return

def grab_author(token):
    location = 'NA'
    employments = 'NA'
    gender = 'NA'
    educations = 'NA'
    status_code = 0

    if len(token) != 0:
        author_url = 'https://www.zhihu.com/api/v4/members/' + token
        try:
            res = requests.get(author_url, headers=headers, params={'include': 'locations,employments,gender,educations'})
            status_code = res.status_code
        except ConnectionError as e:
            print(e)

        print('author {0}'.format(status_code))
        if res.status_code == 200:
            author = res.json()
            #print(author)

            try:
                arr = [loc['name'] for loc in author['locations']]
                if len(arr) > 0:
                    location = ' '.join(arr)
                arr = [(emp['job']['name'] if 'job' in emp else '') + ':' + (emp['company']['name'] if 'company' in emp else '') for emp in author['employments']]
                if len(arr) > 0:
                    employments = ' '.join(arr)
                gender = '男' if author['gender'] == 1 else '女'
                arr = [(edu['major']['name'] if 'major' in edu else '') + ':' + (edu['school']['name'] if 'school' in edu else '') for edu in author['educations']]
                if len(arr) > 0:
                    educations = ' '.join(arr)
            except KeyError as e:
                print(e)
                print(author)

    return (location, employments, gender, educations)


def test():
    timestamp = 1479883652
    s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    print(s)


if __name__ == "__main__":
    print("Start")
    #test()
    grab("https://www.zhihu.com/api/v4/questions/31606466")

