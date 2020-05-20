from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

r = requests.get('https://www.hltv.org/stats/teams/matches/9085/Chaos?startDate=2020-02-20&endDate=2020-05-20' , headers=headers)
print (r)


soup = BeautifulSoup(r.text, 'html.parser')
results = soup.find_all('tr')
df5 = pd.DataFrame()

cnt=1
for result in results[1:]:
    print ('%s of %s' %(cnt, len(results)-1))
    date = result.contents[1].text
    event = result.contents[3].text
    opponent = result.contents[7].text
    Map = result.contents[9].text
    Score = "'" + result.contents[11].text
    WinorLoss = result.contents[13].text
    PointDifference = eval(result.contents[11].text)



    round_results = result.find('td', {'class':'time'})
    link = round_results.find('a')['href']


    r2 = requests.get('https://www.hltv.org' + link ,headers=headers)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    round_history = soup2.find('div', {'class':'standard-box round-history-con'})

    teams = round_history.find_all('img', {'class':'round-history-team'})
    teams_list = [ x['title'] for x in teams ]



    rounds_winners = {}
    n = 1
    row = round_history.find('div',{'class':'round-history-team-row'})
    for each in row.find_all('img',{'class':'round-history-outcome'}):
        if 'emptyHistory' in each['src']:
            winner = teams_list[1]
            loser = teams_list[0]
        else:
            winner = teams_list[0]
            loser = teams_list[1]

        rounds_winners['Round%02dResult' %n] = winner
        n+=1


    round_row_df = pd.DataFrame.from_dict(rounds_winners,orient='index').T

    temp_df = pd.DataFrame([[date,event,opponent,Map,Score,WinorLoss,PointDifference]],columns=['date','event','opponent','Map','Score','WinorLoss', 'PointDifference'])
    temp_df = temp_df.merge(round_row_df, left_index=True, right_index=True)

    df5 = df5.append(temp_df, sort=True).reset_index(drop=True)
    time.sleep(.1)
    cnt+=1

df5 = df5[['date','event','opponent','Map','Score','WinorLoss','PointDifference', 'Round01Result']]
df5 = df5.rename(columns={'date':'Date',
                          'event':'Event',
                          'WinorLoss':'Result',
                          'PointDifference' : 'Point Difference',
                          'Round01Result':'Round1 Result',
                          })

df5.to_csv('FuriaResults.csv',index=False,encoding='utf-8')