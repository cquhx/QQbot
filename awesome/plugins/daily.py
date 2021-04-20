import pymysql
from nonebot import on_command, CommandSession
import re
from nonebot import on_natural_language, NLPSession, IntentCommand
from jieba import posseg
import random
import datetime


@on_command('searchscore', aliases=('积分查询', '查询积分'), only_to_me=False)
async def searchscore(session: CommandSession):
    user_id = str(session.ctx['sender']['user_id'])
    con = pymysql.connect(host='xxx', user='xxx', password='xxx', database='xxx', charset='utf8')
    cur = con.cursor()
    cur.execute('select score from u where id = %s', user_id)
    res = str(cur.fetchone())
    cur.close()
    con.close()
    s = 0
    for i in res:
        if i != '(' and i != ')' and i != ',':
            s = s*10 + int(i)
    if s:
        await session.send(f'{s}')
        return
    await session.send(f'你还没有分数呢')


@on_command('daily', aliases=('签到', 'daily'), only_to_me=False)
async def daily(session: CommandSession):
    user_id = str(session.ctx['sender']['user_id'])
    a = random.randint(1, 50)
    con = pymysql.connect(host='localhost', user='root', password='sql171015', database='qqbot', charset='utf8')
    cur = con.cursor()
    s = 'select da from u where id = %s' % user_id
    cur.execute(s)
    con.commit()
    res = str(cur.fetchone())
    k = ''
    for i in res:
        if i.isdigit() or i == '-':
            k += i
    today = str(datetime.date.today())
    if k == today:
        await session.send('你今天已经签过到了', at_sender=True)
    else:
        s = "insert into u values('{}','{}','{}') on DUPLICATE key update score=score+'{}',da='{}'".\
            format(user_id, a, today, a, today)
        cur.execute(s)
        con.commit()
        await session.send(f'获得积分:{a}', at_sender=True)
    cur.close()
    con.close()


