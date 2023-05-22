import json
# from scrapy.http import Request
import requests
import re


class WeiboRequest(object):
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Cookie': ''
    }  # 通过检查网页获取代理信息和cookie

    # 基于微博用户id 来请求用户数据。
    def getContent(self, tweet_id):
        # 这里user_ids可替换成实际待采集的数据
        # tweet_ids = ['LqlZNhJFm']
        print(tweet_id)
        url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
        print(url)
        # yield Request(url, callback=self.parse)
        response = self.request(url)
        item = self.parse(response)
        print(item)
        return item

    def parse(self, response):
        """
        网页解析
        """
        data = json.loads(response.text)
        print(data)
        item = self.parse_tweet_info(data)

        return item

    def parse_tweet_info(self,data):
        """
        解析推文数据
        """
        tweet = {
            "_id": str(data['mid']),
            "mblogid": data['mblogid'],
            # "created_at": parse_time(data['created_at']),
            "geo": data['geo'],
            "ip_location": data.get('region_name', None),
            "reposts_count": data['reposts_count'],
            "comments_count": data['comments_count'],
            "attitudes_count": data['attitudes_count'],
            "source": data['source'],
            "content": data['text_raw'].replace('\u200b', ''),
            # "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
            # "pic_num": data['pic_num'],
            # 'isLongText': False,
            # "user": parse_user_info(data['user']),
        }
        # if '</a>' in tweet['source']:
        #     tweet['source'] = re.search(
        #         r'>(.*?)</a>', tweet['source']).group(1)
        #     # tweet['source'] = 'sr'
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

    def parse_long_tweet(response):
        """
        解析长推文
        """
        data = json.loads(response.text)['data']
        item = response.meta['item']
        item['content'] = data['longTextContent']
        return item

    def request(self, url):
        resp =requests.get(url, headers=self.headers)
        return resp

wb = WeiboRequest()
wb.getContent(tweet_id='LqlZNhJFm')