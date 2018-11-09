from bs4 import BeautifulSoup
import requests
import time
import json

urls = ['http://0day.ali213.net/s?kw=&page={}'.format(str(i)) for i in range(109, 1000)]

games_url = []
t = 1000
for url in urls:
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    selects = [
        'body > div.ol_list > div.ol_list_l > div:nth-of-type({}) > div.ol_one_c > div.ol_one_c_tit > h3 > a'.format(
            str(i)) for i in range(1, 11)]
    print(t)
    t += 1

    for i in range(10):
        game_url = soup.find_all(class_='ol_one_c_tit')[i].contents[1].contents[0].get('href')
        game_url = 'http://0day.ali213.net' + game_url
        # game_url = 'http://0day.ali213.net/html/2015/22481.html'
        games_url.append(game_url)

        game_data = requests.get(game_url)
        game_data.encoding = 'utf-8'
        game_soup = BeautifulSoup(game_data.text, 'lxml')

        try:
            cn_name = game_soup.find(class_='xs-c1-c-cn').contents[0].get_text()
        except (AttributeError):
            try:
                cn_name = game_soup.find(class_='xs-c1-c-cn').contents[0]
            except(AttributeError, IndexError, KeyError):
                print(str(i) + ' list other page of 1')
                cn_name = ['']

        try:
            en_name = game_soup.find(class_='xs-c1-c-en').contents[0]
            gtime = game_soup.find(class_='xs-c1-c-time').contents[0].get_text().split('P')[0]
            gtype = game_soup.find_all(class_='xs-c1-c-info-l')[0].contents[0].split('：')[1]
            gmanu = game_soup.find_all(class_='xs-c1-c-info-r')[0].contents[0].split('：')[1]
            giss = game_soup.find_all(class_='xs-c1-c-info-r')[1].contents[0].split('：')[1]
            glangu = game_soup.find_all(class_='xs-c1-c-info-l')[1].contents[1].get_text()
            gplats = game_soup.select('body > div.xs-top > div > div.xs-c1-c > div.xs-c1-c-pt > ul')[0].stripped_strings
            gplat = list(gplats)
        except (AttributeError, IndexError, KeyError):
            print(str(i) + ' other page of 2')
            en_name = ['']
            gtype = ['']
            gtime = ['']
            gmanu = ['']
            giss = ['']
            glangu = ['']
            gplat = ['']

        try:
            intro = game_soup.find(class_='xs-c1-c-con xs-c1-c-tct').contents[0].get_text().strip('\u3000')
        except (AttributeError):
            try:
                intro = game_soup.find(class_='xs-c1-c-con xs-c1-c-tct').contents[0].strip('\u3000')
            except(AttributeError):
                try:
                    intro = game_soup.find(class_='xs-c1-c-con').contents[0].get_text().strip('\u3000')
                except (AttributeError, IndexError, KeyError):
                    print(str(i) + ' other page of 3')
                    intro = ['']

        try:
            tags = game_soup.find(class_='xs-c1-c-tag').stripped_strings
            tag = list(tags)
        except (AttributeError, IndexError, KeyError):
            print(str(i) + ' other page of 4')
            tag = ['']

        try:
            id = game_url.split('/')[-1].split('.')[0]
            rate_url = 'http://0day.ali213.net/getvote_xs.php?Action=Show&OdayID={}'.format(id)
            rate_request = requests.get(rate_url)
            rate = eval(rate_request.text)['data'][1]

        except (AttributeError, IndexError, KeyError):
            print(str(i) + ' other page of 5')
            tag = ['']
            rate = ['']

        data = {
            'cn_name': cn_name,
            'en_name': en_name,
            '上市时间': gtime,
            '游戏类型': gtype,
            '制作公司': gmanu,
            '发行公司': giss,
            '游戏语言': glangu,
            '游戏平台': gplat,
            '游戏简介': intro,
            'tag': tag,
            'rate': rate
        }

        with open('data_v3.json', 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')

            time.sleep(0.5)
