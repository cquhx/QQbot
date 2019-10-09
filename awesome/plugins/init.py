from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from jieba import posseg
import random

from .data import get_weather_of_city
from .data import fff


@on_command('who', aliases=('名字', '姓名', '叫什么'), only_to_me=False)
async def who(session: CommandSession):
    await session.send('My name is "张新昌"')


@on_command('sex', aliases=('性别', "男还是女"), only_to_me=False)
async def sex(session: CommandSession):
    await session.send('secret')


@on_command('daily', aliases=('签到', ''), only_to_me=False)
async def daily(session: CommandSession):
    a = random.randint(1, 3)
    if a == 1:
        str1 = "恭喜您签到成功"+"\n"+"获得积分:"+" "+str(random.randint(1, 100))
        await session.send(str1)
    else:
        await session.send('签到失败,请重新签到')


@on_command('weather', aliases=('天气', '天气预报', '查天气'), only_to_me=False)
async def weather(session: CommandSession):
    city = session.get('city', prompt='你想查询哪个城市的天气呢？')
    weather_report = await get_weather_of_city(city)
    await session.send(weather_report)


@weather.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['city'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要查询的城市名称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg


# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'天气'}, only_to_me=False)
async def _(session: NLPSession):
    # 去掉消息首尾的空白符
    stripped_msg = session.msg_text.strip()
    # 对消息进行分词和词性标注
    words = posseg.lcut(stripped_msg)

    city = None
    # 遍历 posseg.lcut 返回的列表
    for word in words:
        # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
        if word.flag == 'ns':
            # ns 词性表示地名
            city = word.word

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'weather', current_arg=city or '')


@on_command('translate', aliases=('翻译', 'translate'), only_to_me=False)
async def translate(session: CommandSession):
    sentence = session.get('sentence', prompt="你想翻译什么呢?")
    res = await fff(sentence)
    await session.send(res)


@translate.arg_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['sentence'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要翻译的内容称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg

