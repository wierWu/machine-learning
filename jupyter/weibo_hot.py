import requests
from bs4 import BeautifulSoup


class SinaWeiboScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    # 获取热门微博前20条微博的内容、博主姓名、微博类型、博主类型
    def get_hot_weibo(self):
        url = "https://s.weibo.com/top/summary?cate=realtimehot"
        print(url)
        response = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        hot_weibo_list = soup.select(".td-02")
        hot_weibos = []
        print(hot_weibo_list)
        for hot_weibo in hot_weibo_list:
            weibo = {}
            weibo["content"] = hot_weibo.select_one("a").text
            weibo["blogger_name"] = hot_weibo.select_one(".star_name").text
            weibo["weibo_type"] = hot_weibo.select_one(".icon-txt").text
            weibo["blogger_type"] = hot_weibo.select_one(".star_name + span").text
            weibo["weibo_url"] = hot_weibo.select_one("a")["href"]
            hot_weibos.append(weibo)
        return hot_weibos

    # 获取某个热门微博下点赞最多的10条评论
    def get_hot_comments(self, weibo_url):
        response = requests.get(url=weibo_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        comment_list = soup.select(".list_ul > li")
        hot_comments = []
        for comment in comment_list:
            hot_comments.append({
                "comment_content": comment.select_one(".txt").text,
                "like_count": int(comment.select_one(".likenum").text)
            })
        hot_comments = sorted(hot_comments, key=lambda x: x["like_count"], reverse=True)[:10]
        return hot_comments


if __name__ == '__main__':
    sina_weibo_scraper = SinaWeiboScraper()
    hot_weibos = sina_weibo_scraper.get_hot_weibo()
    for weibo in hot_weibos:
        print("-" * 50)
        print("微博内容：", weibo["content"])
        print("博主姓名：", weibo["blogger_name"])
        print("微博类型：", weibo["weibo_type"])
        print("博主类型：", weibo["blogger_type"])
        print("点赞最多的10条评论：")
        hot_comments = sina_weibo_scraper.get_hot_comments("https:" + weibo["weibo_url"])
        for comment in hot_comments:
            print("评论内容：", comment["comment_content"])
            print("点赞数：", comment["like_count"])
            print("-" * 20)
