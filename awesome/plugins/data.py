import urllib.request
import requests
import gzip
import json


Proxies = {
    "http": "http://61.135.217.7:80",
    "https": "https://1118.190.95.26:9001",
}
Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


def get_weather_data(city_name):
    url1 = 'http://wthrcdn.etouch.cn/weather_mini?city='+urllib.parse.quote(city_name)
    weather_data = urllib.request.urlopen(url1).read()
    weather_data = gzip.decompress(weather_data).decode('utf-8')
    weather_dict = json.loads(weather_data)
    return weather_dict


async def get_weather_of_city(city: str) -> str:
    #     # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    weather_dict = get_weather_data(city)
    # 将json数据转换为dict数据
    if weather_dict.get('desc') == 'invilad-citykey':
        return '你输入的城市名有误，或者天气中心未收录你所在城市'
    elif weather_dict.get('desc') == 'OK':
        forecast = weather_dict.get('data').get('forecast')
        str1 = forecast[0].get('type')
        low = forecast[0].get('low')
        high = forecast[0].get('high')
        return f'{city}的天气是...{str1},{low}->{high}'


def translate(word):
    # 有道词典 api
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # 传输的参数，其中 i 为需要翻译的内容
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    # key 这个字典为发送给有道词典服务器的内容
    response = requests.post(url, data=key)
    # 判断服务器是否相应成功
    if response.status_code == 200:
        # 然后相应的结果
        return response.text
    else:
        return "Failed!"


def get_reuslt(repsonse):
    # 通过 json.loads 把返回的结果加载成 json 格式
    result = json.loads(repsonse)
    return result['translateResult'][0][0]['tgt']


async def fff(word: str) -> str:
    list_trans = translate(word)
    # 将json数据转换为dict数据
    x = get_reuslt(list_trans)
    return f'翻译结果为:{x}'

