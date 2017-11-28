#!/usr/bin/env python
import asyncio
import random
import json
import os
import re
import shlex
import math
import itertools
import time
import string
from collections import OrderedDict
import discord
import numpy
import scipy.special
import asteval
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#Adding functions to asteval
aeval = asteval.Interpreter()
aeval.symtable["r_randint"]=random.randint
aeval.symtable["r_randrange"]=random.randrange
aeval.symtable["r_choice"]=random.choice
if hasattr(random,'choices'):
    aeval.symtable["r_choices"]=random.choices
else:
    def f(population, weights=None, k=1):
        """
        Replacement for `random.choices()`, which is only available in Python 3.6+.
        """
        return numpy.random.choice(population, size=k, p=weights)
    aeval.symtable["r_choices"] = f
aeval.symtable["r_shuffle"]=random.shuffle
aeval.symtable["r_sample"]=random.sample
aeval.symtable["r_random"]=random.random

#print(aeval.symtable)
random.seed(os.urandom(64))

#Building myself
myself = {}

with open('settings.json') as data_file:    
    settings = json.load(data_file)
myself['prefix'] = settings['prefix']
myself['charsign'] = settings['charsign']
myself['help'] = settings['help']

with open('characters.json') as data_file:    
    characters = json.load(data_file)
myself['characters'] = characters

with open('statistics.json') as data_file:    
    statistics = json.load(data_file, object_pairs_hook=OrderedDict)
myself['statistics'] = statistics

with open('bookdata.json') as data_file:    
    bookdata = json.load(data_file)
myself['bookdata'] = bookdata

with open('chargen.json') as data_file:    
    chargen = json.load(data_file)
myself['chargen'] = chargen

with open('itemgen.json') as data_file:    
    itemgen = json.load(data_file)
myself['itemgen'] = itemgen

plt.bar([1],[1])
plt.savefig('work.png')
plt.clf()

token = settings['token']

#string concat: 'your %s is in the %s' % (object, location)

client = discord.Client()

class Fairy:
    def __init__(self):
        self.word = 'Watch Out!'
    
    def state(self):
        if self.word == 'Hey!':
            self.word = 'Listen!'
        elif self.word == 'Listen!':
            self.word = 'Watch Out!'
        else:
            self.word = 'Hey!'
        return self.word

myself['navi'] = Fairy()

myself['waiting'] = {}

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def singleRoll(s):
    t = s.split('d')
    if t[0]=='':
        t[0]=1
    else:
        t[0]=int(t[0])
    t[1]=int(t[1])
    return [random.randint(1,t[1]) for i in range(t[0])]

def explodingRoll(s,n=False,test='='):
    t = s.split('d')
    if t[0]=='':
        t[0]=1
    else:
        t[0]=int(t[0])
    t[1]=int(t[1])
    if not(n):
        n = t[1]
    else:
        n = int(n)
    if test=='>':
        def f(x):
            return x>=n
    elif test=='<':
        def f(x):
            return x<=n
    else:
        def f(x):
            return x==n
    out = tab = [random.randint(1,t[1]) for i in range(t[0])]
    while len([x for x in tab if f(x)])>0:
        tab = [random.randint(1,t[1]) for i in range(len([x for x in tab if f(x)]))]
        out += tab
    return out

def diceRoll(s):
    bigmatches = []
    out=[]
    while s.count('('):
        pos=[s.find('(')+1,None]
        while s[pos[0]:pos[1]].find('(')>-1 and s[pos[0]:pos[1]].find('(')<s[pos[0]:pos[1]].find(')'):
            pos[0]=pos[0]+s[pos[0]:pos[1]].find('(')+1
        if s[pos[0]:pos[1]].find(')')>-1: 
            pos[1]=pos[0]+s[pos[0]:pos[1]].find(')')
        if pos[0]-6>-1 and s[pos[0]-6:pos[0]-1] in ['floor','round'] or pos[0]-5>-1 and s[pos[0]-6:pos[0]-1]=='ceil' or pos[0]-4>-1 and s[pos[0]-6:pos[0]-1]=='abs':
            j1='{'
            j2='}'
        else:
            if pos[0]-2<0 or s[pos[0]-2] in ['+','-','*','/','d']:
                j1 = ''
            else:
                j1 = '*'
            if pos[1]+1>=len(s) or s[pos[1]+1] in ['+','-','*','/','d']:
                j2 = ''
            else:
                j2 = '*'
        roll = diceRoll(s[pos[0]:pos[1]])
        s = s[:pos[0]-1]+j1+str(roll[0][1])+j2+s[pos[1]+1:]
        bigmatches = bigmatches + roll[1]
    """
    while s.count('{'):
        pos=[s.find('{')+1,None]
        while s[pos[0]:pos[1]].find('{')>-1 and s[pos[0]:pos[1]].find('{')<s[pos[0]:pos[1]].find('}'):
            pos[0]=s[pos[0]:pos[1]].find('{')+1
        if s[pos[0]:pos[1]].find(')')>-1: 
            pos[1]=s[pos[0]:pos[1]].find('}')
        sub = s[pos[0]:pos[1]]
        if sub.find(','):
            sub = sub.split(',')
            tab = []
            for i in sub:
                tab.append(diceRoll(i)[0][1])
            sub = 
        else:
            
        roll = diceRoll(s[pos[0],pos[1]])
        s = s[:pos[0]-1]+j1+str(roll[0][1])+j2+s[pos[1]+1:]
        bigmatches = bigmatches + roll[1]
    """
    matches = re.findall('floor{[\d.]+}', s)
    matches = re.findall('\d*d\d+!>\d+', s)
    matches = [[i,explodingRoll(i.split('!>')[0],i.split('!>')[1]),'>'] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!<\d+', s)
    matches = [[i,explodingRoll(i.split('!<')[0],i.split('!<')[1]),'<'] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!\d+', s)
    matches = [[i,explodingRoll(i.split('!')[0],i.split('!')[1])] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!', s)
    matches = [[i,explodingRoll(i.split('!')[0])] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+', s)
    matches = [[i,singleRoll(i)] for i in matches]
    bigmatches = bigmatches + matches
    firstpart = s
    for i in matches:
        firstpart = firstpart.replace(i[0],'('+' + '.join([str(x) for x in i[1]])+')',1)
        s = s.replace(i[0],str(sum(i[1])),1)
    out.append(firstpart)
    while re.search(r'\d+\*\*\d+',s):
        match = re.search(r'\d+\*\*\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    while re.search(r'\d+\*\d+|\d+/\d+|\d+%\d+',s):
        match = re.search(r'\d+\*\d+|\d+/\d+|\d+%\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    while re.search(r'\d+\+\d+|\d+-\d+',s):
        match = re.search(r'\d+\+\d+|\d+-\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    out.append(s)
    return [out,bigmatches]
            
def gBinom(n,k):
    if n<0:
        return (-1)**k*scipy.special.binom(-n,k)
    else:
        return scipy.special.binom(n,k)

def diceProb(n,t,d):
    def singleRollSum(j):
        return ((-1)**j)*gBinom(n,j)*gBinom(t-d*j-1,n-1)
    return d**(-n)*sum([singleRollSum(j) for j in range(int((t-n)/d)+1)])

@client.event
async def on_ready():
    global myself
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global myself
    if message.content.startswith(myself['prefix']):
        print(message.content)
        if message.author.id in myself['waiting']:
            if myself['waiting'][message.author.id][0]=='prefix' or myself['waiting'][message.author.id][0]=='charsign':
                thing = myself['waiting'][message.author.id][0]
                if message.content.strip() == myself['prefix']+'Yes':
                    with open('settings.json') as data_file:
                        settings = json.load(data_file)
                    settings[thing] = myself['waiting'][message.author.id][1]
                    with open('settings.json','w') as data_file:
                        json.dump(settings,data_file,indent=4)
                    myself[thing] = settings[thing]
                    await client.send_message(message.channel, thing+" changed to "+myself[thing])
                elif message.content.strip() == myself['prefix']+'No':
                    await client.send_message(message.channel, thing+" change cancelled")
                else:
                    await client.send_message(message.channel, "That was an invalid response. "+thing+" change cancelled.")
                del myself['waiting'][message.author.id]
            elif myself['waiting'][message.author.id][0]=='delete':
                if message.content.strip() == myself['prefix']+'Yes':
                    del myself['characters'][myself['waiting'][message.author.id][1]]
                    with open('characters.json','w') as data_file:
                        json.dump(myself['characters'],data_file,indent=4)
                    await client.send_message(message.channel, 'Character '+myself['waiting'][message.author.id][1]+' deleted. Goodbye, old friend! :cry:')
                elif message.content.strip() == myself['prefix']+'No':
                    await client.send_message(message.channel, "Character deletion cancelled")
                else:
                    await client.send_message(message.channel, "That was an invalid response. Character deletion cancelled.")
                del myself['waiting'][message.author.id]
        elif message.content.startswith(myself['prefix']+'help'):
            await client.send_message(message.author, "<@"+message.author.id+">:\n"+myself['help'].replace('<spec:prefix>',myself['prefix']).replace('<spec:charsign>',myself['charsign']))
        elif message.content.startswith(myself['prefix']+'roll') or message.content.startswith(myself['prefix']+'r '):
            work = message.content.replace(' +','+').replace('+ ','+')
            if message.content.find(myself['charsign']):
                try:
                    twork = message.content.split(myself['charsign'])[1::2]
                    tout = []
                    for i in twork:
                        x = i.split(':')
                        tout.append(myself['characters'][x[0]][x[1]])
                    for i in range(len(twork)):
                        work = work.replace('$'+twork[i]+'$',tout[i])
                except:
                    work = ''
            test = work.split()
            if len(test)<2 or test[1]=='' and len(test)<3:
                await client.send_message(message.channel, '<@'+message.author.id+'>'+" tried to roll, but didn't know how the syntax works!")
            if work.count('`')>1:
                try:
                    initial = '<@'+message.author.id+'>'+ ' calculated '+work
                    if not(initial[len(initial)-1] in ['!','.','?']):
                        initial = initial + '!'
                    await client.send_message(message.channel, initial)
                    rolls = []
                    s = work.split('`')[1:]
                    while len(s)>1:
                        rolls.append(s[0])
                        s = s[2:]
                    out = '<@'+message.author.id+">'s result"
                    if len(rolls)>1:
                        out+='s'
                    out+=':\n'
                    for roll in rolls:
                        evaluation = aeval(roll)
                        out += "`"+roll+'='+str(evaluation)
                        if aeval.error!=[]:
                            out+= " ("+aeval.error[0].msg+")"
                        out+= '`\n'
                    await client.send_message(message.channel, out)
                except Exception as e:
                    print(e)
                    await client.send_message(message.channel, '<@'+message.author.id+'>'+" calculation didn't make any sense to me!")
            else:
                work = work.split()
                if len(work)>2:
                    details = ' '.join(work[2:])
                else:
                    details = ''
                work = work[1]
                initial = '<@'+message.author.id+'>'+ ' rolled '+work
                if details != '':
                    initial += ' for ' + details
                await client.send_message(message.channel, initial)
                result,matches = diceRoll(work)
                out = '<@'+message.author.id+">'s result:`"+result[0]+'='+result[1]+'`'
                await client.send_message(message.channel, out)
                if len(matches)>0:
                    if not('@'+message.author.id in myself['statistics']):
                        myself['statistics']['@'+message.author.id]={}
                    for i in matches:
                        if not(i[0][0].isdigit()):
                            i[0]='1'+i[0]
                        if not(i[0] in myself['statistics']['probability']):
                            if '!' in i[0]:
                                pass
                                """
                                p1,p2 = i[0].split('d')
                                p2,cond = p2.split('!')
                                p1 = int(p1)
                                p2 = int(p2)
                                if cond=='':
                                    cond = p2
                                    def test(x):
                                        return x==cond
                                else:
                                    if cond[0]=='>':
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x>=cond
                                    elif cond[0]=='<':
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x<=cond
                                    else:
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x==cond
                                d=p2**p1
                                myself['statistics']['probability'][i[0]]={}
                                m = p1*p2+1
                                mult = 1/d
                                lim = 5
                                splode = []
                                for j in range(p1,m):
                                    count = [k for k in partition_min_max(j,p1,1,p2)]
                                    volatile = [x for x in count if any(map(test,x))]
                                    stable = [x for x in count if not(any(map(test,x)))]
                                    if len(volatile)>0:
                                        for k in volatile:
                                            volatilemult = numPerms(k)
                                            splode.append([sum(k),len([x for x in k if test(x)]),volatilemult*mult])
                                    if len(stable)>0:
                                        stable = [k for k in map(numPerms,stable)]
                                        stable = sum(stable)
                                        myself['statistics']['probability'][i[0]][str(j)]=stable*mult
                                itercount = 0
                                while itercount<lim:
                                    newsplode = []
                                    for j in splode:
                                        p1 = j[1]
                                        m = p1*p2+1
                                        mult = j[2]*(1/p2**p1)
                                        for k in range(p1,m):
                                            count = [x for x in partition_min_max(k,p1,1,p2)]
                                            volatile = [x for x in count if any(map(test,x))]
                                            stable = [x for x in count if not(any(map(test,x)))]
                                            if len(volatile)>0:
                                                for k in volatile:
                                                    volatilemult = numPerms(j)
                                                    newsplode.append([j[0]+sum(k),len([x for x in k if test(x)]),volatilemult*mult])
                                            if len(stable)>0:
                                                stable = [x for x in map(numPerms,stable)]
                                                stable = sum(stable)
                                                if str(j[0]+k) in myself['statistics']['probability'][i[0]]:
                                                    myself['statistics']['probability'][i[0]][str(j[0]+k)]+=stable*mult
                                                else:
                                                    myself['statistics']['probability'][i[0]][str(j[0]+k)]=stable*mult
                                    splode = newsplode
                                    itercount += 1
                                """
                            else:
                                p1,p2 = i[0].split('d')
                                p1=int(p1)
                                p2=int(p2)
                                myself['statistics']['probability'][i[0]]={}
                                if p1 == 1:
                                    d = p2**p1
                                    for j in range(p1,p1*p2+1):
                                        myself['statistics']['probability'][i[0]][str(j)]=1/d
                                else:
                                    m = p1*p2+1
                                    hold = OrderedDict()
                                    for j in range(p1,p1+math.ceil((m-p1)/2)):
                                        myself['statistics']['probability'][i[0]][str(j)]=hold[str(m-j+p1-1)]=diceProb(p1,j,p2)
                                    hold=list(hold.items())
                                    hold.reverse()
                                    hold=OrderedDict(hold)
                                    myself['statistics']['probability'][i[0]].update(hold)
                        if '!' in i[0]:
                            pass
                        elif i[0] in myself['statistics']['@'+message.author.id]:
                            myself['statistics']['@'+message.author.id][i[0]][str(sum(i[1]))] += 1
                            myself['statistics']['@'+message.author.id][i[0]]['rolls'] += 1
                        else:
                            myself['statistics']['@'+message.author.id][i[0]]={}
                            myself['statistics']['@'+message.author.id][i[0]]['rolls']=1
                            for j in myself['statistics']['probability'][i[0]].keys():
                                myself['statistics']['@'+message.author.id][i[0]][j]=0
                            myself['statistics']['@'+message.author.id][i[0]][str(sum(i[1]))] += 1
                    with open('statistics.json','w') as data_file:    
                        json.dump(myself['statistics'],data_file,indent=4)
        elif message.content.startswith(myself['prefix']+'poke'):
            await client.send_message(message.channel, myself['navi'].state())
        elif message.content.startswith(myself['prefix']+'poll'):
            await client.add_reaction(message,"\N{THUMBS UP SIGN}")
            await client.add_reaction(message,"\N{THUMBS DOWN SIGN}")
            await client.add_reaction(message,"\U0001F937")
        elif message.content.startswith(myself['prefix']+'statistics'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, '<@'+message.author.id+'>: You need to look up someone in particular')
            else:
                if "<@" in work[1]:
                    lookup = work[1][1:-1]
                    try:
                        mentioned = message.server.get_member(lookup[1:])
                        mentioned = mentioned.nick
                        if not(mentioned):
                            raise ValueError('No nickname')
                    except:
                        mentioned = await client.get_user_info(lookup[1:])
                        mentioned = mentioned.name
                else:
                    if work[1].lower()=="myself":
                        mentioned = message.author.name
                        lookup = '@'+message.author.id
                    else:
                        mentioned = work[1]
                        if message.server:
                            lookup = "@"+message.server.get_member_named(work[1])
                        else:
                            lookup = "@"+message.channel.recipients[0].id
                if not(lookup):
                    await client.send_message(message.channel, '<@'+message.author.id+">: There doesn't seem to be a member of this server that goes by "+mentioned+'.')
                else:
                    if lookup in myself['statistics']:
                        stats = myself['statistics'][lookup]
                        probs = myself['statistics']['probability']
                        if len(work)==2:
                            await client.send_message(message.channel, '<@'+message.author.id+'>: Results for '+mentioned+"'s rolls.\n")
                            for i,j in stats.items():
                                n = j['rolls']
                                t = [[],[]]
                                for k,l in j.items():
                                    if k!='rolls':
                                        t[0].append(int(k))
                                        t[1].append(l/n)
                                if len(t[0])>100:
                                    plt.plot(t[0],t[1],'b-')
                                else:
                                    plt.bar(t[0],t[1])
                                plt.savefig('work.png')
                                plt.clf()
                                await client.send_file(message.channel, 'work.png',content="Recorded "+i)
                                if 'image' in probs[i]:
                                    await client.send_file(message.channel, probs[i]['image'],content="Expected "+i)
                                else:
                                    t = [[],[]]
                                    for k,l in probs[i].items():
                                        t[0].append(int(k))
                                        t[1].append(l)
                                    if len(t[0])>100:
                                        plt.plot(t[0],t[1],'b-')
                                    else:
                                        plt.bar(t[0],t[1])
                                    plt.savefig('Probabilities/'+i+'.png')
                                    plt.clf()
                                    await client.send_file(message.channel,'Probabilities/'+i+'.png',content="Expected "+i)
                                    probs[i]['image']='Probabilities/'+i+'.png'
                                    with open('statistics.json','w') as data_file:    
                                        json.dump(myself['statistics'],data_file,indent=4)
                        else:
                            await client.send_message(message.channel, '<@'+message.author.id+'>: Results for '+mentioned+"'s rolls of "+work[2]+".\n")
                            if work[2] in stats:
                                s="Recorded "+work[2]+":\n"
                                n = stats[work[2]]['rolls']
                                t = [[],[]]
                                for i,j in stats[work[2]].items():
                                    if i!='rolls':
                                        t[0].append(int(i))
                                        t[1].append(j/n)
                                plt.bar(t[0],t[1])
                                plt.savefig('work.png')
                                plt.clf()
                                await client.send_file(message.channel, 'work.png',content="Recorded "+work[2])
                                if 'image' in probs[work[2]]:
                                    await client.send_file(message.channel ,probs[work[2]]['image'],content="Expected "+work[2])
                                else:
                                    t = [[],[]]
                                    for i,j in probs[work[2]].items():
                                        t[0].append(int(i))
                                        t[1].append(j)
                                    plt.bar(t[0],t[1])
                                    plt.savefig('Probabilities/'+i+'.png')
                                    plt.clf()
                                    await client.send_file(message.channel,'Probabilities/'+i+'.png',content="Expected "+work[2])
                                    probs[work[2]]['image']='Probabilities/'+work[2]+'.png'
                                    with open('statistics.json','w') as data_file:    
                                        json.dump(myself['statistics'],data_file,indent=4)
                            else:
                                await client.send_message(message.channel, '<@'+message.author.id+'>: '+mentioned+" doesn't seem to have ever rolled "+work[2]+".")
                    else:
                        await client.send_message(message.channel, '<@'+message.author.id+'>: '+mentioned+" doesn't have any rolls on record")
        elif message.content.startswith(myself['prefix']+'ref'):
            test = message.content.split(" ",2)
            if len(test)==3 and test[1] in myself['bookdata'].keys():
                bookdata = myself['bookdata'][test[1]]
                work = (test[0],test[2])
            else:
                bookdata = myself['bookdata']['all']
                work = message.content.split(" ",1)
            poss = bookdata.keys()
            poss = process.extractOne(work[1], poss)
            if poss[1]>80: 
                await client.send_message(message.channel, bookdata[poss[0]])
            else:
                await client.send_message(message.channel, "Sorry <@"+message.author.id+">, I couldn't find a good match.")
        elif message.content.startswith(myself['prefix']+'prefix') or message.content.startswith(myself['prefix']+'charsign'):
            work = message.content.split()
            thing = work[0][len(myself['prefix']):]
            if len(work)==1:
                if message.author.server_permissions.administrator:
                    await client.send_message(message.channel, "<@%s>: My current %s is %s. If you'd like to change it, type %sprefix <new prefix>"%(message.author.id,thing,myself[thing],myself['prefix']))
                else:
                    await client.send_message(message.channel, "<@%s>: My current %s is %s. If you'd like to change it, you'll have to ask an administrator."%(message.author.id,thing,myself[thing]))
            elif len(work)==2:
                if message.author.server_permissions.administrator:
                    myself['waiting'][message.author.id]=[thing,work[1]]
                    await client.send_message(message.channel, '<@%s>: My current %s is %s. Are you sure you want to change it to "%s"? Use %sYes or %sNo'%(message.author.id,thing,myself[thing],work[1],myself['prefix'],myself['prefix']))
                else:
                    await client.send_message(message.channel, "I'm afraid I can't do that, <@%s>. Only administrators can change my prefix."%(message.author.id))
            else:
                await client.send_message(message.channel, "My "+thing+"s can't have spaces.")
        elif message.content.startswith(myself['prefix']+'chargen'):
            work = shlex.split(message.content)
            raceList={'human':['religion','build','appearance'],
                      'changeling':['true age','apparent gender','apparent ancestry','quirk'],
                      'clockwork':['purpose','form','appearance'],
                      'dwarf':['build','hatred','appearance'],
                      'goblin':['build','habit','odd habit','distinctive appearance','appearance'],
                      'orc':['build','appearance']}
            race = [i for i in work if 'race=' in i.lower() or 'ancestry=' in i.lower()]
            if len(race)==0:
                race = random.choice(['human','changeling','clockwork','dwarf','goblin','orc'])
            else:
                race = race[0].split('=')[1].lower()
                if not(race in raceList):
                    race = random.choice(['human','changeling','clockwork','dwarf','goblin','orc'])
            attributes = ['name','background','personality','age','gender','wealth','thing'] + raceList[race]
            givenList={}
            statmods = {}
            while len(work)>0:
                if work[0].find('=')!=-1:
                    print(work[0])
                    w = work[0].split('=')
                    if w[0].lower() in attributes:
                        givenList[w[0].lower()]=w[1]
                work=work[1:]
            #Name
            char = "Name: "
            if 'name' in givenList:
                char+=givenList['name']+'\n'
            elif race=='clockwork':
                char+=''.join(random.choices(string.ascii_uppercase,k=random.randint(2,5)))+''.join(random.choices(string.digits,k=random.randint(3,7)))+'\n'
            else:
                char+=random.choice(myself['chargen']['name'][race])+'\n'
            #Gender
            if race=='changeling':
                char+='Apparent '
            elif race=='clockwork':
                char+='Voice '            
            char+='Gender: '
            if 'apparent gender' in givenList:
                char+=givenList['apparent gender']+'\n'
            elif 'gender' in givenList:
                char+=givenList['gender']+'\n'
            else:
                if race=='clockwork':
                    char+=random.choice(['Male','Female','Indeterminate'])+'\n'
                else:
                    char+=random.choice(['Male','Female'])+'\n'
            #Age
            if race=='changeling':
                char+='True '
            char+='Age: '
            if 'true age' in givenList:
                char+=givenList['true age']+'\n'
            elif 'age' in givenList:
                char+=givenList['age']+'\n'
            else:
                char+=random.choice(myself['chargen']['age'][race])+'\n'
            intro = char
            char = ''
            #Changling info
            if race=='changeling':
                char+='Apparent Ancestry: '
                if 'apparent ancestry' in givenList:
                    char+= givenList['apparent ancestry']+"\n"
                    app=givenList['apparent ancestry'].lower()
                else:
                    i = random.randint(0,5)+random.randint(0,5)+random.randint(0,5)
                    if i<5:
                        char+= "Goblin\n"
                        app = 'goblin'
                    elif i<8:
                        char+= "Dwarf\n"
                        app = 'dwarf'
                    elif i<16:
                        char+= "Human\n"
                        app = 'human'
                    elif i<18:
                        char+= "Orc\n"
                        app = 'orc'
                    else:
                        char+= "GM's choice\n"
                        app = None
                char += 'Quirk: '
                if 'quirk' in givenList:
                    try:
                        s = int(givenList['quirk'])-1
                        char+=myself['chargen']['quirk'][s]+'\n'
                    except:
                        char+=givenList['quirk']
                else:
                    char+=random.choice(myself['chargen']['quirk'])+'\n'
                if app and app in ['goblin','dwarf','human','orc']:
                    char+='Apparent Age: '
                    char+=random.choice(myself['chargen']['age'][app])+'\n'
                    char+='Apparent Build: '
                    char+=random.choice(myself['chargen']['build'][app])+'\n'
                    char+='Appearance: '
                    s = random.choice(myself['chargen']['appearance'][app])
                    while s.find('[[')>-1:
                        w = s[s.find('[[')+2:s.find(']]')]
                        last = eval(w)
                        w = str(last)
                        s = s[:s.find('[[')]+w+s[s.find(']]')+2:]
                    char+=s+'\n'
            #Build/Form
            if race!='changeling':
                if race=='clockwork':
                    char+='Form: '
                    if 'form' in givenList:
                        value = givenList['form']
                    elif 'build' in givenList:
                        value = givenList['build']
                    else:
                        value = random.randint(0,5)+random.randint(0,5)+random.randint(0,5)
                    try:
                        i = int(value)-3
                        if i == 3:
                            char+="You are a small winged clockwork. Reduce your Health by 5 and your Size to 1/2. You can fly, but you must land at the end of your movement or fall. You are 3 feet tall and weigh 50 pounds."
                            if 'Health' in statmods:
                                statmods['Health']-=5
                            else:
                                statmods['Health']=-5
                            statmods['Size']=0.5
                        elif i<6:
                            char+="You are a small spider-like clockwork with functional hands. Reduce your Size to 1/2. You ignore the effects of difficult terrain when you climb. You are 3 feet tall and weigh 50 pounds."
                            statmods['Size']=0.5
                        elif i<10:
                            char+="You are a small humanoid clockwork. Reduce your Size to 1/2. You are 4 feet tall and weigh 75 pounds."
                            statmods['Size']=0.5
                        elif i<16:
                            char+="You are a humanoid clockwork. You are 6 feet tall and weigh 300 pounds."
                        elif i<18:
                            char+="You are a large humanoid clockwork. Increase your Size to 2, but reduce your Speed and your Defense by 2. You are 10 feet tall and weigh 750 pounds."
                            if 'Speed' in statmods:
                                statmods['Speed']-=2
                            else:
                                statmods['Speed']=-2
                            if 'Defense' in statmods:
                                statmods['Defense']-=2
                            else:
                                statmods['Defense']=-2
                            statmods['Size']=2
                        else:
                            char+="You are a large clockwork with the lower body of a horse. Increase your Size to 2 and your Speed by 2. However, reduce your Defense by 3. You are 6 feet long, 6 feet tall, and weigh 750 pounds."
                            if 'Speed' in statmods:
                                statmods['Speed']+=2
                            else:
                                statmods['Speed']=2
                            if 'Defense' in statmods:
                                statmods['Defense']-=3
                            else:
                                statmods['Defense']=-3
                            statmods['Size']=2
                        char+='\n'
                    except:
                        char+=value+"\n"
                else:
                    char+='Build: '
                    if 'build' in givenList:
                        try:
                            s=random.choice(myself['chargen']['build'][race])
                        except:
                            s=givenList['build']
                        char+=s+'\n'
                    else:
                        char+=random.choice(myself['chargen']['build'][race])+'\n'
            #Appearance
            if race!='changeling':
                char+='Appearance: '
                if 'appearance' in givenList:
                    try:
                        i = int(char)
                    except:
                        char+=givenList['appearance']+'\n'
                        i = "string"
                else:
                    i=None
                if i!='string':
                    if isinstance(i,int):
                        if race=='goblin':
                            i-=1
                        else:
                            i-=3
                    elif race=='goblin':
                        i = random.randint(0,19)
                    else:
                        i = random.randint(0,5)+random.randint(0,5)+random.randint(0,5)
                    work = myself['chargen']['appearance'][race][i]
                    while work.find('[[')>-1:
                        w = work[work.find('[[')+2:work.find(']]')]
                        last = eval(w)
                        w = str(last)
                        work = work[:work.find('[[')]+w+work[work.find(']]')+2:]
                    char+=work+'\n'
            #Race Specific
            if race=='human':
                char += 'Religion: '
                if 'religion' in givenList:
                    try: 
                        s = myself['chargen']['religion'][int(givenList['religion'])-3]
                        char += s + '\n'
                    except:
                        char += givenList['religion'] + '\n'
                else:
                    char += random.choice(myself['chargen']['religion']) + '\n'
            elif race=='clockwork':
                char += 'Purpose: '
                if 'purpose' in givenList:
                    try: 
                        s = myself['chargen']['purpose'][int(givenList['purpose'])-1]
                        char += s + '\n'
                    except:
                        char += givenList['purpose'] + '\n'
                else:
                    char += random.choice(myself['chargen']['purpose']) + '\n'
            elif race=='dwarf':
                char += 'Hatred: '
                if 'hatred' in givenList:
                    try: 
                        s = myself['chargen']['hatred'][int(givenList['hatred'])-1]
                        char += s + '\n'
                    except:
                        char += givenList['hatred'] + '\n'
                else:
                    char += random.choice(myself['chargen']['hatred']) + '\n'
            elif race=='goblin':
                char += 'Odd Habit: '
                if 'odd habit' in givenList:
                    try: 
                        s = myself['chargen']['habit'][int(givenList['odd habit'])-1]
                        char += s + '\n'
                    except:
                        char += givenList['odd habit'] + '\n'
                elif 'habit' in givenList:
                    try: 
                        s = myself['chargen']['habit'][int(givenList['habit'])-1]
                        char += s + '\n'
                    except:
                        char += givenList['habit'] + '\n'
                else:
                    char += random.choice(myself['chargen']['habit']) + '\n'
            #Background
            char+='Background: '
            if 'background' in givenList:
                try:
                    work=myself['chargen']['background'][int(givenList['background'])-1]
                except:
                    work=givenList['background']
            else:
                work=random.choice(myself['chargen']['background'][race])
            if not ('background' in givenList) or work!=givenList['background']:
                extra = False
                if isinstance(work,list):
                    extra = work[1]
                    work = work[0]
                while work.find('[[')>-1:
                    w = work[work.find('[[')+2:work.find(']]')]
                    if extra and w == extra[1]:
                        last = extra[1] = eval(w)
                        w = str(extra[1])
                    else:
                        last = eval(w)
                        w = str(last)
                    work = work[:work.find('[[')]+w+work[work.find(']]')+2:]
                if extra:
                    if extra[0] in statmods:
                        statmods[extra[0]]+=extra[1]
                    else:
                        statmods[extra[0]]=extra[1]
                    if len(extra)>2:
                        if extra[2] in statmods:
                            statmods[extra[2]]+=extra[3]
                        else:
                            statmods[extra[2]]=extra[3]
            char += work + "\n"
            #Personality
            char+='Personality: '
            if 'personality' in givenList:
                try:
                    char+=myself['chargen']['personality'][int(givenList['personality'])-1]+ "\n"
                except:
                    char+=givenList['personality']+ "\n"
            else:
                char+=random.choice(myself['chargen']['personality'][race])+ "\n"
            stats = myself['chargen']['attributes'][race]
            if 'Strength' in statmods:
                stats['Strength']+=statmods['Strength']
            if race=='human':
                stats['Perception']=stats['Intellect']
                stats['Defense']=stats['Agility']
                stats['Health']=stats['Strength']
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1/2 or 1"
                stats['Speed']=10
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=0
                stats['Languages and Professions']="Spoken Common, along with one additional profession or language, before any other bonuses."
            elif race=='changeling':
                stats['Perception']=stats['Intellect']+1
                stats['Defense']=stats['Agility']
                stats['Health']=stats['Strength']
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1"
                stats['Speed']=10
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=0
                stats['Languages and Professions']="Spoken Common, before any other bonuses."
                stats['Immunities']="Damage from disease; charmed, diseased."
                stats['Additional Traits']="Iron Vulnerability, Shadowsight, Steal Identity"
            elif race=='clockwork':
                stats['Perception']=stats['Intellect']
                stats['Defense']=13
                stats['Health']=stats['Strength']
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1"
                stats['Speed']=8
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=0
                stats['Languages and Professions']="Spoken Common, before any other bonuses."
                stats['Immunities']="Damage from disease and poison; asleep, diseased, fatigued, poisoned."
                stats['Additional Traits']="Key, Mechanical Body, Repairing Damage"
            elif race=='dwarf':
                stats['Perception']=stats['Intellect']+1
                stats['Defense']=stats['Agility']
                stats['Health']=stats['Strength']+4
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1/2"
                stats['Speed']=8
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=0
                stats['Languages and Professions']="Spoken Common, Spoken and Written Dwarfish, before any other bonuses."
                stats['Additional Traits']="Darksight, Hated Creature, Robust Constitution"
            elif race=='goblin':
                stats['Perception']=stats['Intellect']+1
                stats['Defense']=stats['Agility']
                stats['Health']=stats['Strength']
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1/2"
                stats['Speed']=10
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=0
                stats['Languages and Professions']="Spoken Common, Spoken Elvish, before any other bonuses."
                stats['Immunities']="Damage from disease; charmed, diseased"
                stats['Additional Traits']="Iron Vulnerability, Shadowsight, Sneaky"
            elif race=='orc':
                stats['Perception']=stats['Intellect']+1
                stats['Defense']=stats['Agility']
                stats['Health']=stats['Strength']
                stats['Healing Rate']=math.floor(stats['Health']/4)
                stats['Size']="1"
                stats['Speed']=12
                stats['Power']=0
                stats['Damage']=0
                stats['Insanity']=0
                stats['Corruption']=1
                stats['Languages and Professions']="Spoken Common, Spoken Dark Speech, before any other bonuses."
                stats['Additional Traits']="Shadowsight"
            if 'Insanity' in statmods:
                stats['Insanity']+=statmods['Insanity']
            if 'Corruption' in statmods:
                stats['Corruption']+=statmods['Corruption']
            intro+='Ancestry: '+race.title()+'\n'
            for i in ["Strength","Agility","Intellect","Will",'Bonus','Perception','Defense','Health','Healing Rate','Size','Speed','Power','Damage','Insanity','Corruption','Languages and Professions','Immunities','Additional Traits']:
                if i in stats:
                    intro+=i+': '+str(stats[i])+'\n'
            char = intro+char+'Wealth: '
            if 'wealth' in givenList:
                try:
                    s = myself['chargen']['wealth'][int(givenList['wealth'])]
                    char+=s
                except:
                    char+=givenList['wealth']
            else:
                char+=random.choice(myself['chargen']['wealth'])
            char+='\nInteresting Thing: '
            char+=random.choice(myself['chargen']['thing'])
            if len(char)>2000:
                while char!='':
                    i=char[:2000].rfind('\n')
                    await client.send_message(message.channel, char[:i])
                    char = char[i+1:]
            else:
                await client.send_message(message.channel, char)
        elif message.content.startswith(myself['prefix']+'itemgen'):
            work = shlex.split(message.content)[1:]
            attributes=['form','properties','desc']
            results={'form':0,'properties':0,'desc':0}
            while len(work)>0:
                if work[0].find('=')!=-1:
                    w = work[0].split('=')
                    if w[0].lower() in attributes:
                        try:
                            int(w[1])
                            results[w[0].lower()]=int(w[1])
                work=work[1:]
            for i,j in results.items():
                if j==0:
                    results[i]=randint(1,20)
            results['properties']=math.floor(results['properties']/4)
            output = 'Item Form: '+myself['itemgen']['form'][results['form']-1]+'\n'
            output += 'Item Description: '+myself['itemgen']['desc'][results['properties']][results['desc']-1]
            await client.send_message(message.channel, output)
        elif message.content.startswith(myself['prefix']+'newchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'newchar usage: '+myself['prefix']+'newchar [character name] <attributes>')
            else:
                char = work[1]
                if char in myself['characters']:
                    await client.send_message(message.channel, "That character already exists; use editattr to change attributes.")
                else:
                    myself['characters'][char]={'__creator__':message.author.id,'__hidden__':False}
                    work = work[2:]
                    while len(work)>0:
                        if work[0].find('=')!=-1:
                            w = work[0].split('=')
                            if not(w[0] in ['__creator__']) and w[0].find('!')!=0:
                                myself['characters'][char][w[0]]=w[1]
                        elif work[0].find(':')!=-1:
                            w = work[0].split('=')
                            if not(w[0] in ['__creator__']) and w[0].find('!')!=0:
                                myself['characters'][char][w[0]]=w[1]
                        work = work[1:]
                    with open('characters.json','w') as data_file:
                        json.dump(myself['characters'],data_file,indent=4)
                    await client.send_message(message.channel, char + " created! Use "+myself['prefix']+"editattr to change attributes, or "+myself['prefix']+"viewchar to view.")
        elif message.content.startswith(myself['prefix']+'viewchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'viewchar usage: '+myself['prefix']+'viewchar [character name] <attribute>')
            else:
                char = work[1]
                if char in myself['characters'] and (not(myself['characters'][char]['__hidden__']) or message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator):
                    if len(work)==3:
                        if work[2] in myself['characters'][char]:
                            await client.send_message(message.channel, "%s's %s attribute: %s"%(char,work[2],myself['characters'][char][work[2]]))
                        else:
                            await client.send_message(message.channel, "%s doesn't have an attribute called %s."%(char,work[2]))
                    else:
                        await client.send_message(message.channel, char+" is a character created by <@"+ myself['characters'][char]['__creator__'] +"> with the following attributes:") 
                        attrs = []
                        for i,j in myself['characters'][char].items():
                            if not(i in ["__creator__",'__hidden__']):
                                attrs.append(i)
                        if attrs==[]:
                            attrs="None"
                        elif len(attrs)==1:
                            attrs = attrs[0]
                        elif len(attrs)==2:
                            attrs = attrs[0]+' and '+attrs[1]
                        else:
                            attrs = ', '.join(attrs[:-1])+', and '+attrs[-1]
                        await client.send_message(message.channel, attrs)    
                else:
                    await client.send_message(message.channel, "That character does not exist, or is hidden.") 
        elif message.content.startswith(myself['prefix']+'hidechar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'hidechar usage: '+myself['prefix']+'hidechar [character name]')
            else:
                char = work[1]
                if char in myself['characters'] and (message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator):
                    myself['characters'][char]['__hidden__'] = not(myself['characters'][char]['__hidden__'])
                    if myself['characters'][char]['__hidden__']:
                        await client.send_message(message.channel, char + " hidden.")
                    else:
                        await client.send_message(message.channel, char + " unhidden.")
                else:
                    await client.send_message(message.channel, "That character does not exist, or does not belong to you.") 
        elif message.content.startswith(myself['prefix']+'delchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'delchar usage: '+myself['prefix']+'delchar [character name]')
            else:
                char = work[1]
                if char in myself['characters']:
                    if message.author.id == myself['characters'][char]['__creator__']:
                        await client.send_message(message.channel, 'Are you sure you want to delete your character %s? Use %sYes or %sNo'%(char,myself['prefix'],myself['prefix']))
                        myself['waiting'][message.author.id]=['delete',char]
                    elif message.author.server_permissions.administrator:
                        await client.send_message(message.channel, "Are you sure you want to delete %s's character %s? Use %sYes or %sNo"%(myself['characters'][char]['__creator__'],char,myself['prefix'],myself['prefix']))
                        myself['waiting'][message.author.id]=['delete',char]
                    else:
                        await client.send_message(message.channel, char+' belongs to <@'+myself['characters'][char]['__creator__']+'>. Only the creator or an administrator can delete them.')
                else:
                    await client.send_message(message.channel, "That character does not exist.") 
        elif message.content.startswith(myself['prefix']+'editattr'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'editattr usage: '+myself['prefix']+'editattr [character name] <attributes>')
            else:
                char = work[1]
                if char in myself['characters']:
                    if message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator:
                        work = work[2:]
                        while len(work)>0:
                            if work[0].find('!')==0:
                                w = work[0][1:]
                                if w in myself['characters'][char]:
                                    del myself['characters'][char][w]
                            elif work[0].find('=')!=-1:
                                w = work[0].split('=')
                                if not(w[0] in ["__creator__",'__hidden__']):
                                    print(w)
                                    myself['characters'][char][w[0]]=w[1]
                            elif work[0].find(':')!=-1:
                                w = work[0].split(':')
                                if not(w[0] in ["__creator__",'__hidden__']):
                                    print(w)
                                    myself['characters'][char][w[0]]=w[1]
                            work = work[1:]
                        with open('characters.json','w') as data_file:
                            json.dump(myself['characters'],data_file,indent=4)
                        await client.send_message(message.channel, char + " edited!")
                    else:
                        await client.send_message(message.channel, char+' belongs to <@'+myself['characters'][char]['__creator__']+'>. Only the creator or an administrator can edit them.')
                else:
                    await client.send_message(message.channel, "That character does not exist; use newchar to create them.") 
sleeptime=0
sleeptimes=[5,5,30,60,60*5]
while True:
    try: 
        client.loop.run_until_complete(client.start(token))
    except discord.errors.LoginFailure as e:
        print("The client failed to login with error: "+e.args[0])
        if e.args[0]=="Improper token has been passed.":
            print("Did you put a valid token into settings.json?")
            break
    except BaseException as e
        print("Something went wrong:") 
        print("Error: "+e.args[0])
        time.sleep(sleeptimes[sleeptime])
        if sleeptime<4:
            sleeptime+=1