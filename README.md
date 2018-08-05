# Selenium+PhantomJS爬取淘宝美食

搜索关键字：利用Selenium驱动浏览器搜索关键字，得到查询后的商品列表

分析页码并翻页：得到商品页码数，模拟翻页，得到后续页面的商品列表

分析提取商品内容：利用PyQuery分析源码，解析得到商品列表

存储至MongoDB：将商品列表信息存储到数据库MongoDB

总结思考

1.一开始使用显示等待访问，通过CSS_SELECTOR的id选择器找到网页元素，可最后程序都执行异常，每次都是TimeoutExceptions的异常错误。经过反复排查，才发现淘宝网有很多个站点，我在程序中使用的http://www.taobao.com，但是在进行网页分析的时候随意用百度搜了一个淘宝站点，它的站点是https://uland.taobao.com/sem/tbsearch。两个站点地址不一样，网页元素也不一样，自己竟然会犯这种错误，应牢记

2.text参数是否在该span元素内，此处需要注意text的参数位置
text_to_be_present_in_element(locator, text_)
