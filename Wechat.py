#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/11 11:20
# @Author  : ChenHuan
# @Site    : 
# @File    : Wechat.py
# @Desc    :
# @Software: PyCharm
import re
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib import cm
from matplotlib import colors
import matplotlib as mpl
import time
import pandas
from pyecharts import Map
from pyecharts import Geo
import numpy as np
# from PIL import Image
from matplotlib.font_manager import *
from wordcloud import WordCloud
# 安装词云 conda install -c conda-forge wordcloud
import TencentYoutuyun
from TencentYoutuyun import conf
# 安装腾讯优图 pip insatll Python_sdk-master.zip
import jieba
from jieba import analyse
import snownlp
from scipy.misc import imread
import itchat
# 微信网页版接口封装Python版本,它很好的兼容了wechat个人账号的API接口,让我们能更加便捷的爬取wechat数据

def wechat_login():
    """
    微信登录
    :return:
    """
    itchat.login()
    # 爬取自己好友相关信息,返回一个json文件
    friends = itchat.get_friends(update=True)[0:]
    # print(friends)
    # 将friends写入文件，以后就不用每次调试都要登陆网页版了
    file = open('weChatFriendArealDistribution.json', 'w',
                encoding='utf-8')
    json.dump(friends, file, ensure_ascii=False)
    file.close()

# 读取json 文件
openfile = open('weChatFriendArealDistribution.json', 'r',
                encoding='utf-8')
loadFriends = json.load(openfile)
# 解决matplotlib图例中文乱码:https://www.zhihu.com/question/25404709/answer/309806474
# zhfont = FontProperties(fname='C:\Windows\Fonts\simkai.ttf')

def analyse_sex(friends):
    """
    分析好友性别
    :param friends:
    :return:
    """
    sex = list(map(lambda x : x['Sex'], friends[1:]))
    # print(sex)
    counts = list(map(lambda x : x[1], Counter(sex).items()))
    # print(Counter(sex))
    # print(Counter(sex).items())
    # print(counts)
    # lables = ['Unknown', 'Male', 'Female']
    lables = [u'未知', u'男性', u'女性']
    colors = ['skyblue', 'yellow', 'red']
    # 将某部分爆炸出来,使用括号,将第一块分割出来,数值的大小是分割出来的与其他两块的间隙
    explode = (0, 0.05, 0)
    plt.figure(figsize=(9, 6), dpi=80)
    plt.axes(aspect=1)
    plt.pie(counts, explode=explode, labels=lables, colors=colors, labeldistance=1.1, autopct='%3.1f%%',
            shadow=False, startangle=90, pctdistance=0.6)
    # 性别统计结果,性别展示标签,饼图区域配色,标签距离圆点距离,饼图区域文本格式,饼图是否显示阴影,饼图起始角度,饼图区域文本距离圆点距离
    plt.legend()
    plt.title(u'%s的好友性别比例' % friends[0]['NickName'])
    # plt.legend(prop=zhfont)
    plt.show()

def analyse_head_image(friends):
    """
    分析好友头像,从两个方面来分析:
        第一,在这些好友头像中,使用人脸头像的好友比重有多大;
        第二,从这些好友头像中,可以提取出哪些有价值的关键字
    :param friends:
    :return:
    """
    # 初始路径
    path = os.path.abspath('.')
    folder = path + '\\HeadImages\\'
    if(os.path.exists(folder) == False):
        os.makedirs(folder)

    # 人脸检测
    """
    - 接口
        `DetectFace(self, image_path, mode = 0, data_type = 0)`
    - 参数
    	- `image_path` 待检测的图片路径
	    - `mode` 是否大脸模式，默认非大脸模式
        - `data_type` 用于表示image_path是图片还是url, 0代表图片，1代表url
    """
    use_face = 0
    not_use_face = 0
    img_tags = ''
    # 申请应用密钥
    appid = '10130514' #平台添加应用后分配的AppId
    secret_id = 'AKIDVvAIyUd690gEbrhylNp7xbIsJYcVwnGZ' #平台添加应用后分配的SecretId
    secret_key = 'HNJ4e5LPL9mEVbVEm9KLG1eAWgfT6Yqy' #平台添加应用后分配的SecretKey
    end_point = TencentYoutuyun.conf.API_YOUTU_END_POINT
    youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, end_point)
    # 保存头像
    for index in range(1, len(friends)):
        friend = friends[index]
        img_file = folder + '\\Image%s.jpg' % str(index)
        # print(friend['UserName'])
        # 从json文件中读取数据时,无需登录此处会报错,则先注释,第一次保存头像需要解开注释
        # img_data = itchat.get_head_img(userName=friend['UserName'])
        # if (os.path.exists(img_file) == False):
        #     print(img_file)
        #     with open(img_file, 'wb') as f:
        #         f.write(img_data)
        time.sleep(1)
        # 检测头像
        result1 = youtu.DetectFace(image_path = img_file ,mode = 0,data_type = 0)
        if result1['face']:
            use_face += 1
        else:
            not_use_face += 1
        # 图像标签识别 imagetag(self, image_path, data_type = 0, seq = '')
        result2 = youtu.imagetag(image_path = img_file, data_type = 0, seq = '')
        print(index, '>>>>', result2)
        img_tags += ','.join(list(map(lambda x : x['tag_name'], result2['tags'])))

    lables = [u'人脸头像', u'非人脸头像']
    counts = [use_face, not_use_face]
    colors = ['skyblue', 'yellow']
    # 将某部分爆炸出来,使用括号,将第一块分割出来,数值的大小是分割出来的与其他两块的间隙
    explode = (0, 0.05)
    plt.figure(figsize=(9, 6), dpi=80)
    plt.axes(aspect=1)
    plt.pie(counts, explode=explode, labels=lables, colors=colors, labeldistance=1.1, autopct='%3.1f%%',
            shadow=False, startangle=90, pctdistance=0.6)
    # 头像统计结果,头像展示标签,饼图区域配色,标签距离圆点距离,饼图区域文本格式,饼图是否显示阴影,饼图起始角度,饼图区域文本距离圆点距离
    plt.legend()
    plt.title(u'%s的好友头像情况' % friends[0]['NickName'])
    plt.show()

    img_tags = img_tags.encode('iso8859-1').decode('utf-8')
    print(img_tags)
    # 读取背景图
    # 两种方式 img_back = np.array(Image.open("imagename.png"))
    img_back = imread('steve.jpg')
    wordcloud = WordCloud(background_color='white',  # 背景图片中不添加word的颜色
                          max_words=2000,  # 最大词个数
                          mask=img_back,
                          font_path='E:\Web-Crawler\Wechat\SimHei.ttf',
                          # 设置字体格式,如不设置显示不了中文,而且字体名不能是中文
                          max_font_size=60,  # 设置字体大小的最大值
                          random_state=100,
                          scale=1.5,
                          )
    wordcloud.generate(img_tags)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    wordcloud.to_file('img_tags.jpg')

def analyse_Signature(friends):
    """
    分析好友签名
    :param friends:
    :return:
    """
    signatures = ''
    emotions = []
    for friend in friends:
        signature = friend['Signature']
        print(signature)
        if signature != None:
            signature = signature.strip().replace('span', '').replace('class', '').replace('emoji', '')
            signature = re.sub(r'1f(\d.+)', '', signature)
            print('signature>>>', signature)
        if len(signature) > 0:
            # 权值
            nlp = snownlp.SnowNLP(signature)
            emotions.append(nlp.sentiments)
            # 关键字提取
            signatures += ' '.join(jieba.analyse.extract_tags(signature, 5))
            print('signatures>>>', signatures)
    # 标签名词云图
    # 读取背景图
    img_back = imread('heart.png')
    wordcloud = WordCloud(background_color='white',  # 背景图片中不添加word的颜色
                          max_words=2000,  # 最大词个数
                          mask=img_back,
                          font_path='E:\Web-Crawler\Wechat\SimHei.ttf',
                          # 设置字体格式,如不设置显示不了中文,而且字体名不能是中文
                          max_font_size=45,  # 设置字体大小的最大值
                          random_state=30,
                          scale=1.5,
                          )
    wordcloud.generate(signatures)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    wordcloud.to_file('signatures.jpg')
    # 情感比重反应人生观
    positive = len(list(filter(lambda x : x > 0.66, emotions)))
    negative = len(list(filter(lambda x : x < 0.33, emotions)))
    neutral = len(list(filter(lambda x : x >= 0.33 and x <= 0.66, emotions)))
    lables = [u'积极', u'中性', u'消极']
    values = [positive, negative, neutral]
    # plt.rcParams['font.sans-serif'] = ['simHei']
    # plt.rcParams['axes.unicode_minus'] = False
    plt.xlabel('情感判断')
    plt.ylabel('频数')
    plt.xticks(range(3), lables)
    plt.legend(loc='upper right')
    plt.bar(range(3), values, color = 'rgb')
    plt.title(u'%s好友的情感分析' % friends[0]['NickName'])
    plt.show()

def get_attr(friends, key):
    """
    工具函数,获取对应属性值
    :param friends:
    :param key:
    :return:
    """
    return list(map(lambda x : x.get(key), friends))


# noinspection PyStatementEffect
def analyse_location(friends):
    """
    分析好友地理位置
    :param friends:
    :return:
    """
    friend = dict(province = get_attr(friends, 'Province'),
                  city = get_attr(friends, 'City'),
                  nickname = get_attr(friends, 'NickName'))
    print('friend>>>', friend)
    province = pandas.DataFrame(friend)
    print('province>>>', province)
    provinces = province.groupby('province', as_index = True)['province'].count().sort_values()
    print('provinces>>>', provinces)
    # 未填写地址的改为未知
    unknow = list(map(lambda x : x if x != '' else '未知', list(provinces.index)))
    value = list(provinces)
    _map = Map('微信好友位置分布图', title_pos='center', width=1000, height=500)
    _map.add('', unknow, value, is_label_show = True, is_visualmap = True, visual_text_color='#000', visual_range=[0,120])
    _map.render('provinces.html')

# 定义一个函数,用来爬取各个变量,return list arr
def get_var(var):
    variable = []
    for i in loadFriends:
        value = i[var]
        variable.append(value)
    return variable

def analyse_provice():
    """
    好友地图分布
    :return:
    """
    Province = get_var('Province')
    City = get_var('City')
    print(City)
    provinceCount = Counter(Province)
    cityCount = Counter(City)
    print('cityCount>>>', cityCount)
    print('provinceCount>>>', provinceCount)
    # print(provinceCount)
    # print(list(provinceCount.elements()))
    # print(sorted(provinceCount.elements()))
    # print(list(provinceCount.values()))
    # print(sum(provinceCount.values()))  # 381
    # print(len(Province)) # 381
    # print(len(provinceCount)) # 37
    # for key in provinceCount.elements():
    #     print(key, provinceCount[key])
    totalCount = len(cityCount)
    pName = []
    pNum = []
    pPercent = []
    for each in provinceCount.items():
        # (a, b) = each
        # print(a, b)
        pName.append(each[0])
        pNum.append(each[1])
        pPercent.append(each[1] / totalCount)
    # print(pName)
    # print(pNum)
    # print(matplotlib.matplotlib_fname())
    # /usr/local/lib/python3.6/site-packages/matplotlib/mpl-data/matplotlibrc
    # from matplotlib.font_manager import _rebuild
    #
    # _rebuild()
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # font = FontProperties(fname='/Library/Fonts/Songti.ttc') # 该方法未验证
    # 1.柱状图
    plt.figure(figsize=(12, 6))
    # plt.bar(range(len(pNum)), pNum, tick_label=pName, align="center", alpha=0.9, width = 1.0, facecolor = 'skyblue', edgecolor = 'white', label='one', lw=6)
    plt.barh(range(len(pNum)), pNum, tick_label=pName, align="center", alpha=0.9, facecolor='skyblue',
            edgecolor='white', label='one', lw=3)
    plt.xlabel(u"人数")
    plt.ylabel(u"地区")
    plt.title(u"地区比例分析")
    plt.legend((u"图例",))
    plt.show()
    # 2.饼状图
    labels = pName
    fracs = pPercent
    # explode = [0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #            0]  # 0.1 凸出这部分，共len(provinceCount)=37个
    # plt.axes(aspect=1)  # set this , Figure is round, otherwise it is an ellipse
    # # autopct ，show percet
    # plt.pie(x=fracs, labels=labels, autopct='%3.1f %%',
    #         shadow=False, labeldistance=1.1, startangle=90, pctdistance=0.6)
    # plt.show()
    #
    # fig1, ax1 = plt.subplots(figsize=(12, 9))  # 设置绘图区域大小
    #
    # a = np.random.rand(1, 19)
    # color_vals = list(a[0])
    # my_norm = mpl.colors.Normalize(-1, 1)  # 将颜色数据的范围设置为 [0, 1]
    # my_cmap = mpl.cm.get_cmap('rainbow', len(color_vals))  # 可选择合适的colormap，如：'rainbow'
    #
    # patches, texts, autotexts = ax1.pie(fracs, labels=labels, autopct='%1.0f%%',
    #                                     shadow=False, startangle=170, colors=my_cmap(my_norm(color_vals)))
    #
    # ax1.axis('equal')
    #
    # # 重新设置字体大小
    # proptease = fm.FontProperties()
    # proptease.set_size('xx-small')
    # # font size include: ‘xx-small’,x-small’,'small’,'medium’,‘large’,‘x-large’,‘xx-large’ or number, e.g. '12'
    # plt.setp(autotexts, fontproperties=proptease)
    # plt.setp(texts, fontproperties=proptease)
    #
    # # plt.savefig('Demo_project_set_color_1.jpg')
    # plt.show()

    fig, ax = plt.subplots(figsize=(12, 6))  # 设置绘图区域大小

    colors = cm.rainbow(np.arange(len(fracs)) / len(fracs))  # colormaps: Paired, autumn, rainbow, gray,spring,Darks
    patches, texts, autotexts = ax.pie(fracs, labels=labels, autopct='%1.0f%%',
                                       shadow=False, startangle=170, colors=colors)

    ax.axis('equal')
    ax.set_title('微信好友位置分布图', loc='left')

    # 重新设置字体大小
    proptease = fm.FontProperties()
    proptease.set_size('xx-small')
    # font size include: ‘xx-small’,x-small’,'small’,'medium’,‘large’,‘x-large’,‘xx-large’ or number, e.g. '12'
    plt.setp(autotexts, fontproperties=proptease)
    plt.setp(texts, fontproperties=proptease)

    # plt.savefig('wechat_pie.jpg')
    plt.show()

    # fig, axes = plt.subplots(figsize=(8, 5), ncols=2)  # 设置绘图区域大小
    # ax1, ax2 = axes.ravel()
    #
    # colors = cm.rainbow(np.arange(len(fracs)) / len(fracs))  # colormaps: Paired, autumn, rainbow, gray,spring,Darks
    # patches, texts, autotexts = ax1.pie(fracs, labels=labels, autopct='%1.0f%%',
    #                                     shadow=False, startangle=170, colors=colors, labeldistance=1.2,
    #                                     pctdistance=1.03, radius=0.4)
    # # labeldistance: 控制labels显示的位置
    # # pctdistance: 控制百分比显示的位置
    # # radius: 控制切片突出的距离
    #
    # ax1.axis('equal')
    #
    # # 重新设置字体大小
    # proptease = fm.FontProperties()
    # proptease.set_size('xx-small')
    # # font size include: ‘xx-small’,x-small’,'small’,'medium’,‘large’,‘x-large’,‘xx-large’ or number, e.g. '12'
    # plt.setp(autotexts, fontproperties=proptease)
    # plt.setp(texts, fontproperties=proptease)
    #
    # ax1.set_title('Shapes', loc='center')
    #
    # # ax2 只显示图例（legend）
    # ax2.axis('off')
    # ax2.legend(patches, labels, loc='center left')
    #
    # plt.tight_layout()
    # # plt.savefig("pie_shape_ufo.png", bbox_inches='tight')
    # # plt.savefig('Demo_project_final.jpg')
    # plt.show()
    # # 3.地图
    # value = pNum
    # attr = pName
    # print('attr>>>', attr)
    # print('value>>>', value)
    # geo = Geo("我的好友分布图", width=1200, height=600)
    # geo.add("各城市分布情况", attr, value, type="effectScatter", symbol_size=20, border_color="#ffffff",
    #         is_label_show=True, label_text_color="#00FF00", label_pos="inside", symbol="circle",
    #         symbol_color="FF0000", geo_normal_color="#006edd", geo_emphasis_color="#0000ff")
    # geo.show_config()
    # # geo.render("friendProvinceDistribution.html")
    # geo.render("friendCityDistribution.html")

if __name__ == '__main__':
    wechat_login()
    analyse_sex(loadFriends)
    analyse_head_image(loadFriends)
    analyse_Signature(loadFriends)
    # analyse_location(loadFriends)
    analyse_provice()