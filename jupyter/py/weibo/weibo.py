import json
import requests
import re
import dateutil.parser

class WeiboApi(object):
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Cookie': 'SINAGLOBAL=5704367839825.553.1624008237316; _ga=GA1.2.1649937523.1628073066; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWZijOI4V.31XG.I5pXf64v5JpX5KMhUgL.Fo2R1hn7S054ehM2dJLoI7UNIgHETgSV; WBPSESS=yqshitLUXpXGaKtyJ_VzBFuK2LuXMfS7o5h-m66bvWEw1UmGlLf45OxuynuQ6srYrVuw8cL1wa27GDgr2U0P1ytb0aOoBhqpWs_R4X8nkv7ph0hQungLHrJ-EIiWiS9Wn4moyHJcExwLyIe80SYn9w==; XSRF-TOKEN=wC6SZP1yh0Sq5pQyeeMn7L49; ALF=1687313820; SSOLoginState=1684721824; SCF=AgF60GHp7VAdMHeXI3Aswv0-UN0S6Ua9LupIg9vqctZHOx_rUe6DXs_wfp4s3wtlJe7szfn4tlL-FK9uOxUeieM.; SUB=_2A25JbqDxDeRhGedG41oR9y7FyzuIHXVqHZU5rDV8PUNbmtANLXb7kW9NUOu8HF0RLtjtTaH7L7sUBcbM0JU3pkUa; _s_tentry=weibo.com; Apache=2940413414701.0107.1684722004598; ULV=1684722004603:26:3:2:2940413414701.0107.1684722004598:1684681517157; UOR=,,www.google.com.hk'
    }  # 通过检查网页获取代理信息和cookie

    def request(self, url):
        resp =requests.get(url, headers=self.headers)
        return resp
    
    def get_user_weibo_info(self,uid=None,screen_name=None):
        user = self.get_user(uid=uid,screen_name=screen_name)
        weibos = self.get_user_weibo_list(user['id'])
        user_weibo_info ={
            'user':user,
            'weibolist':weibos
        }
        return user_weibo_info

    #获取用户信息
    def get_user(self,uid=None,screen_name=None):
        url = f'https://weibo.com/ajax/profile/info?uid={uid}'
        if not uid:
            url =  f'https://weibo.com/ajax/profile/info?screen_name={screen_name}'
        # print(url)
        response = self.request(url)
        data = json.loads(response.text)
        user = data['data']['user']
        # print('url:{},user:{}',url,user)
        return user

    # 获取用户的微博列表,只获取一页
    def get_user_weibo_list(self,uid):
        url = f"https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1"
        response = self.request(url)
        data = json.loads(response.text)
        tweets = data['data']['list']
        weibo_list = []
        i=0
        for tweet in tweets:
            item = self.parse_tweet_info(tweet)
            weibo_list.append(item)
            i=i+1
            if i>10:
                break
        return weibo_list
    
    def get_weibo_comment_list(self,mid):
        url = f"https://weibo.com/ajax/statuses/buildComments?" \
              f"is_reload=1&id={mid}&is_show_bulletin=2&is_mix=0&count=3"
        response = self.request(url)
        data = json.loads(response.text)
        comment_list = []
        for comment_info in data['data']:
            item = self.parse_comment(comment_info)
            comment_list.append(item)
        return comment_list

    def parse_tweet_info(self,data):
        """
        获取评论列表
        """
        comment_list = self.get_weibo_comment_list(data['mid'])
        """
        解析推文数据
        """
        tweet = {
            "mid": str(data['mid']),
            "mblogid": data['mblogid'],
            "created_at": self.parse_time(data['created_at']),
            "geo": data['geo'],
            "ip_location": data.get('region_name', None),
            "reposts_count": data['reposts_count'],
            "comments_count": data['comments_count'],
            "attitudes_count": data['attitudes_count'],
            # "source": data['source'],
            "content": data['text_raw'].replace('\u200b', ''),
            # "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
            # "pic_num": data['pic_num'],
            'isLongText': False,
            'comments':comment_list
        }
        # if '</a>' in tweet['source']:
        #     tweet['source'] = re.search(r'>(.*?)</a>', tweet['source']).group(1)
     
        # if 'page_info' in data and data['page_info'].get('object_type', '') == 'video':
        #     media_info = None
        #     if 'media_info' in data['page_info']:
        #         media_info = data['page_info']['media_info']
        #     elif 'cards' in data['page_info'] and 'media_info' in data['page_info']['cards'][0]:
        #         media_info = data['page_info']['cards'][0]['media_info']
        #     if media_info:
        #         tweet['video'] = media_info['stream_url']
        # tweet['url'] = f"https://weibo.com/{tweet['user']['_id']}/{tweet['mblogid']}"
        # if 'continue_tag' in data and data['isLongText']:
        #     tweet['isLongText'] = True
        return tweet

    def parse_time(self,s):
        """
        Wed Oct 19 23:44:36 +0800 2022 => 2022-10-19 23:44:36
        """
        return dateutil.parser.parse(s).strftime('%Y-%m-%d %H:%M:%S')

    def parse_comment(self,data):
        """
        解析comment
        """
        item = dict()
        # item['created_at'] = self.parse_time(data['created_at'])
        item['_id'] = data['id']
        item['like_counts'] = data['like_counts']
        item['ip_location'] = data['source']
        item['content'] = data['text_raw']
        # item['comment_user'] = parse_user_info(data['user'])
        return item


# weibo = WeiboApi()
# info = weibo.get_user_weibo_info(uid=6512991534,screen_name='吃花椒的喵酱')
# print(info)