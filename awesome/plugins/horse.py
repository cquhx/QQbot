import pymysql
from nonebot import on_command, CommandSession
from nonebot import permission
import nonebot
from nonebot.typing import Context_T
import time
import re
import random


dic = {}
flag = True
flag1 = False
horses = ["🦍", "🦆", "🦀", "🐉", "🐎"]
dis = [25, 25, 25, 25, 25]
num = {}
winner = 0


def showhorse():
    s = ""
    for i in range(0, 5):
        s += str(i + 1) + '|' + dis[i] * ' ' + horses[i]
        if i < 4:
            s += '\n'
    return s


def judge():
    temp = []
    global winner
    win = True
    for i in range(5):
        if dis[i] <= 0:
            temp.append(i + 1)
            win = False
    if len(temp):
        a = random.randint(0, int(len(temp) - 1))
        winner = temp[a]
    return win


@on_command('start', aliases=('比赛开始', '赛马开始'), permission=permission.GROUP_ADMIN)
async def start(session: CommandSession):
    global flag
    global flag1
    global winner
    flag = False
    con = pymysql.connect(host='localhost', user='root', password='xxx', database='xxx', charset='utf8')
    cur = con.cursor()
    if flag1:
        flag1 = False
        flag = True
        while judge():
            for i in range(5):
                dis[i] -= random.randint(1, 5)
            s = showhorse()
            await session.send(f'{s}')
            time.sleep(3)
        await session.send(f'恭喜{winner}号获得胜利!')
        users = [k for k, v in dic.items() if v == winner]
        for i in users:
            print(num[i])
            cur.execute("update u set score=score+'{}' where id = '{}'".format(num[i] * 100, i))
            con.commit()
            await session.send(f'恭喜[CQ:at,qq={i}] 获得{num[i]*100}积分')
    cur.close()
    con.close()


bot = nonebot.get_bot()
nums = []


@bot.on_message('group')
async def group_msg(ctx: Context_T):
    global flag1
    if not flag1:
        return
    s = str(ctx['message'])
    user_id = str(ctx['sender']['user_id'])
    if s.isdigit() and int(s) in range(1, 6):
        if flag:
            s = int(s)
            con = pymysql.connect(host='localhost', user='root', password='xxx', database='xxx', charset='utf8')
            cur = con.cursor()
            if not (user_id in dic):
                dic[user_id] = s
                num[user_id] = 1
            elif dic[user_id] != s:
                dic[user_id] = s
                num[user_id] = 1
            else:
                num[user_id] += 1
            cur.execute('select score from u where id = %s', user_id)
            res = str(cur.fetchone())
            con.commit()
            s = 0
            for i in res:
                if i != '(' and i != ')' and i != ',':
                    s = s*10 + int(i)
            temp = random.randint(15, 25)
            if s < temp:
                await bot.send(ctx, "你的分数不够呢,请获取积分后重试")
            else:
                cur.execute("update u set score=score-'{}' where id = '{}'".format(temp, user_id))
                con.commit()
                await bot.send(ctx, f'下注成功,扣除积分{temp}')
            cur.close()
            con.close()


@on_command('horse', aliases=('赛马', ''), permission=permission.GROUP_ADMIN)
async def horse(session: CommandSession):
    global flag1
    global dis
    flag1 = True
    dis = [25, 25, 25, 25, 25]
    s = ""
    for i in num:
        num[i] = 1
    for i in dic:
        dic[i] = 0
    for i in range(0, 5):
        s += str(i+1) + '|' + dis[i]*' ' + horses[i]
        if i < 4:
            s += '\n'
    await session.send(f'{s}')


@on_command('cal', aliases=('算24', '24'), only_to_me=False)
async def cal(session: CommandSession):
    nums.clear()
    a = random.randint(1, 10)
    nums.append(a)
    b = random.randint(1, 10)
    nums.append(b)
    c = random.randint(1, 10)
    nums.append(c)
    d = random.randint(1, 10)
    nums.append(d)
    nums.sort()
    await session.send(f'{a} {b} {c} {d}')


def compare(op1, op2):
    return op1 in ["*", "/"] and op2 in ["+", "-"]


def getvalue(num1, num2, operator):
    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    else:
        return num1 / num2


def process(data, opt):
    operator = opt.pop()
    num2 = data.pop()
    num1 = data.pop()
    data.append(getvalue(num1, num2, operator))


def calculate(s):
    data = []  # 数据栈
    opt = []  # 操作符栈
    i = 0  # 表达式遍历索引
    while i < len(s):
        if s[i].isdigit():  # 数字，入栈data
            start = i  # 数字字符开始位置
            while i + 1 < len(s) and s[i + 1].isdigit():
                i += 1
            data.append(int(s[start: i + 1]))  # i为最后一个数字字符的位置
        elif s[i] == ")":  # 右括号，opt出栈同时data出栈并计算，计算结果入栈data，直到opt出栈一个左括号
            while opt[-1] != "(":
                process(data, opt)
            opt.pop()  # 出栈"("
        elif not opt or opt[-1] == "(":  # 操作符栈为空，或者操作符栈顶为左括号，操作符直接入栈opt
            opt.append(s[i])
        elif s[i] == "(" or compare(s[i], opt[-1]):  # 当前操作符为左括号或者比栈顶操作符优先级高，操作符直接入栈opt
            opt.append(s[i])
        else:  # 优先级不比栈顶操作符高时，opt出栈同时data出栈并计算，计算结果如栈data
            while opt and not compare(s[i], opt[-1]):
                if opt[-1] == "(":  # 若遇到左括号，停止计算
                    break
                process(data, opt)
            opt.append(s[i])
        i += 1  # 遍历索引后移
    while opt:
        process(data, opt)
    return data.pop()


@bot.on_message('group')
async def group_msg(ctx: Context_T):
    s = str(ctx['message'])
    n = len(s)
    if re.match("\(?\d{1,2}\)?[+\-*/]\(?\d{1,2}\)?[+\-*/]\(?\d{1,2}\)?[+\-*/]\(?\d{1,2}\)?", s):
        flag2 = False
        whole = []
        i = 0
        while i < n:
            if s[i].isdigit():
                if i + 1 < n and s[i+1].isdigit():
                    whole.append(10)
                    i += 1
                else:
                    whole.append(int(s[i]))
            i += 1
        whole.sort()
        print(whole)
        print(nums)
        if not nums == whole:
            await bot.send(ctx, "你搞个屁")
            return
        s = calculate(s)
        if s == 24:
            await bot.send(ctx, "恭喜解决")
            con = pymysql.connect(host='localhost', user='root', password='xxx', database='xxx', charset='utf8')
            cur = con.cursor()
            user_id = str(ctx['sender']['user_id'])
            cur.execute("update u set score=score+100 where id = '{}'".format(user_id))
            con.commit()
            cur.close()
            con.close()







