#!/usr/bin/env python
import pandas
from binance.client import Client
import numpy as np
import time
import telegram
import emoji
from pyti.relative_strength_index import relative_strength_index as rsi
from pyti.average_true_range import average_true_range as atr
from requests import Request, Session
import json

class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """
    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)

if __name__ == '__main__':
    credentials = '/PATH/Credentials'
    dompath = '/PATH/BTCDOM'
    hashpath = '/PATH/HashRatio'
    markets = '/PATH/Markets'
    buyvalue4h = '/PATH/BuyValue4h'
    report ='/PATH/Report4h'
    connection = BinanceConnection(credentials)
    interval = '4h'
    limit = 500
    bot = telegram.Bot(token="<TOKEN>") #Telegram Bot Token
    chatid = "CHATID" #Telegram Chatid
    fireemoji = emoji.emojize(':fire:')
    shitemoji = '\U0001F4A7'
    thumbsup = '\U0001F44D'
    thumbsdown = '\U0001F44E'
    while True:
        #time.sleep(20)
        try:
            with open(markets) as fp:
                lines = fp.read().splitlines()
                bvalue4h = open(buyvalue4h, "w")
                rp = open(report, "r")
                dom = open(dompath, "r")
                hr = open(hashpath, "r")

                count = 0
                try:
                   for line in lines:
                        symbol = lines[count]
                        try:
                           klines = connection.client.get_klines(symbol=symbol, interval=interval, limit=limit)
                           open = [float(entry[1]) for entry in klines]
                           high = [float(entry[2]) for entry in klines]
                           low = [float(entry[3]) for entry in klines]
                           close = [float(entry[4]) for entry in klines]
                           volume = [float(entry[7]) for entry in klines]
                           buyavg = ((close[-1] + high[-1]) / 2.03 - (high[-1] * (1 - open[-1] / close[-1]) * (1 - ((close[-1] * open[-1]) / (high[-1] * close[-1])))))
                           sellavg = (low[-1] + close[-1]) / 1.99 + (low[-1] * (1 - low[-1] / open[-1]) * (1 - ((low[-1] * open[-1]) / (close[-1] * high[-1]))) / 1.1)
                           volumeratio = volume[-1]/volume[-2]
                           rsivalue = rsi(close,14)
                           atrvalue = atr(close,4)
                           rsiicon = ''
                           last_closing_price = close[-1]
                           sloss = close[-1]-(atrvalue[-1]*1.7)# (low[-1]+close[-2]+close[-3]+close[-4])/4
                           if sloss < buyavg*0.93 or sloss > buyavg*0.99:
                            sloss=buyavg*0.93
                           close_array = np.asarray(close)
                           last4 = close_array[-5:]
                           donchianconversionline = (last4.max() + last4.min())/2
                           close_finished = close_array[:-1]
                           emax = pandas.DataFrame(close_array)
                           ema1=8
                           ema2=20
                           last_ema1 = emax.ewm(span=ema1).mean().iloc[-1,-1]
                           last_ema2 = emax.ewm(span=ema2).mean().iloc[-1,-1]
                           previous_ema1 = emax.ewm(span=ema1).mean().iloc[-2,-1]
                           previous_ema2 = emax.ewm(span=ema2).mean().iloc[-2,-1]
                           intervalfibo = '4h'
                           klinesfibo = connection.client.get_klines(symbol=symbol, interval=intervalfibo, limit=limit)
                           closefibo = [float(entry[4]) for entry in klinesfibo]
                           fibo_array = np.asarray(closefibo)
                           df = fibo_array[-126:]
                           maxr = df.max()
                           minr = df.min()
                           diff = maxr - minr
                           level0 = maxr - (0*diff)     #level 0 tepe noktası
                           level1 = maxr - (0.236*diff) #%236short
                           level2 = maxr - (0.382*diff) #%382 önemli direnç/destek (SHORT)
                           level3 = maxr - (0.5*diff)   #%50
                           level4 = maxr - (0.618*diff) #%618 önemli direnç destek (LONG)
                           level5 = maxr - (0.786*diff) #%786 alt destek
                           level6 = maxr - (1*diff)     #%1 dip destek
                           levela = maxr + (0.382*diff) #tepe1
                           levelb = maxr + (0.618*diff) #tepe2
                           level = 0
                           x = close[-1]
                           far = 0
                           seviye = ""
                           dip = ""
                           if x < level0 and x > level1:
                            level = 1
                            candlel = "\U0001F531"
                            far = (x - level1)/level1
                            seviye = "\nTargets: " + str("{:.8f}".format(level0))+", "+str("{:.8f}".format(levela))+", "+ str("{:.8f}".format(levelb))+"+"
                            dip = level1
                           elif x < level1 and x > level2:
                            level = 2
                            candlel = "\U0001F531"*2
                            far = (x - level2)/level2
                            seviye = "\nTargets: " + str("{:.8f}".format(level1))+", "+str("{:.8f}".format(level0))+", "+ str("{:.8f}".format(levela))+"+"
                            dip = level2
                           elif x < level2 and x > level3:
                            level = 3
                            candlel = "\U0001F531"*3
                            far = (x - level3)/level3
                            seviye = "\nTargets: " + str("{:.8f}".format(level2))+", "+str("{:.8f}".format(levela))+", "+ str("{:.8f}".format(levelb))+"+"
                            dip = level3
                           elif x < level3 and x > level4:
                            level = 4
                            candlel = "\U0001F531"*4
                            far = (x - level4)/level4
                            seviye = "\nTargets: " + str("{:.8f}".format(level2))+'\U0001F530'+", "+str("{:.8f}".format(level1))+", "+ str("{:.8f}".format(level0))+"+"
                            dip = level4
                           elif x < level4 and x > level5:
                            level = 5
                            candlel = "\U0001F531"*5
                            far = (x - level5)/level5
                            seviye = "\nTargets: " + str("{:.8f}".format(level4))+'\U0001F530'+", "+str("{:.8f}".format(level2))+'\U0001F530'+", "+ str("{:.8f}".format(level1))+"+"
                            dip = level5
                           elif x < level5 and x > level6:
                            level = 6
                            candlel = "\U0001F531"*6
                            far = (x - level6)/level6
                            seviye = "\nTargets: " + str("{:.8f}".format(level4))+'\U0001F530'+", "+str("{:.8f}".format(level3))+", "+ str("{:.8f}".format(level2))+"\U0001F530+"
                            dip = level6
                           elif x < level6:
                            level = 7
                            candlel = "\U0001F531"*7
                            seviye = "\nTargets: " + str("{:.8f}".format(level5))+", "+str("{:.8f}".format(level4))+'\U0001F530'+", "+ str("{:.8f}".format(level2))+"\U0001F530+"
                            dip = level7
                           else:
                            level = "belirlenemedi!"
                            far = (x - level7)/level7
                           if close[-1]< buyavg:
                            buyavg=close[-1]
                           if dip > buyavg:
                            dip = buyavg*0.99
                           fibolevel = "\U0001F4CA FİBONACCI SEVİYELERİ(21 günlük) -Şu anki seviyesi: "+str(level)+" "+candlel+" Alt seviyeye uzaklık: "+str("{0:.4%}".format(far))+"\nTepe-2: "+str("{:.8f}".format(levelb)) +"\nTepe-1: "+str("{:.8f}".format(levela))+ "\nSeviye 0: "+str("{:.8f}".format(level0))+": Tepe noktası %0 \U0001F4B2 \n"+"Seviye 1: "+str("{:.8f}".format(level1))+": Direnç/Destek noktası %236\n"+"Seviye 2: "+str("{:.8f}".format(level2))+": Önemli Direnç/Destek noktası(SHORT)  %382 \U0001F4AA \n"+"Seviye 3: "+str("{:.8f}".format(level3))+": Ara nokta %50\n"+"Seviye 4: "+str("{:.8f}".format(level4))+": Önemli Direnç/Destek noktası(LONG) %618 \U0001F4AA \n"+"Seviye 5: "+str("{:.8f}".format(level5))+": Alt Destek noktası %786\n"+"Seviye 6: "+str("{:.8f}".format(level6))+": Dip Destek noktası %1\n"
                           def telegramsat(id):
                            bot.sendMessage(chat_id=id, text=(shitemoji*3)+ "SAT (TOP 200) 4 Saatlik Grafik (EMA"+str(ema1)+"-"+str(ema2)+ ")\n" + symbol +"\nŞu anki değer: " +str("{:.8f}".format(close[-1])) +"\nSatış girilecek değer: "+str("{:.8f}".format(sellavg))+ "\n4 saatlik dilimdeki düşüş oranı: "+str("{0:.4%}".format(ratiodown))+ thumbsdown +"\nEMA'ya Uzaklık: "+str("{0:.4%}".format(ratioEMAdown))+emojiema+ "\nHacim "+str("{:.1f}".format(volumeratio))+ " kat arttı!\n"+candle+fibolevel)
                           def telegramal(id):
                            bot.sendMessage(chat_id=id, text=(fireemoji*1)+"#" +symbol +"\nYou can buy some here!\n"+ "\nCurrent Price: "+ str("{:.8f}".format(close[-1]))+ "\n" + "Buy from this Price: "+str("{:.8f}".format(buyavg))+seviye+"\n\U000026D4Stop Loss: "+str("{:.8f}".format(sloss)))
                            bvalue4h.write(symbol+"\n"+str("{:.8f}".format(buyavg))+"\n")
                           print(symbol,"{:.8f}".format(close[-1]), "{:.8f}".format(last_ema1),"{:.8f}".format(level1),"{:.8f}".format(level4),seviye,"{:.8f}".format(sloss))
                           if last_ema2 > last_ema1 and previous_ema1 > previous_ema2 and ("{:.8f}".format(last_ema1)) > ("{:.8f}".format(level1)):
                            ratiodown=(open[-1] - close[-1])/open[-1]
                            ratioEMAdown=(last_ema1-close[-1])/close[-1]
                            if ratioEMAdown >0 and ratioEMAdown<0.01: emojiema='\U0001F6A9'
                            elif ratioEMAdown>=0.01 and ratioEMAdown<0.03: emojiema=('\U0001F6A9')*2
                            elif ratioEMAdown>=0.03 and ratioEMAdown<0.05: emojiema=('\U0001F6A9')*3
                            elif ratioEMAdown>=0.05 and ratioEMAdown<0.07: emojiema=('\U0001F6A9')*4
                            elif ratioEMAdown>=0.07: emojiema=('\U0001F6A9')*5
                    #        telegramsat(chatid)
                           elif last_ema1 > last_ema2 and previous_ema1 < previous_ema2 and ("{:.8f}".format(last_ema1)) < ("{:.8f}".format(level5)):
                            ratioEMAup=(close[-1]-last_ema1)/last_ema1
                            ratioup=(close[-1]-open[-1])/open[-1]
                            if ratioEMAup >0 and ratioEMAup<0.01: emojiema='\U0001F4B0'
                            elif ratioEMAup>=0.01 and ratioEMAup<0.03: emojiema=('\U0001F4B0')*2
                            elif ratioEMAup>=0.03 and ratioEMAup<0.05: emojiema=('\U0001F4B0')*3
                            elif ratioEMAup>=0.05 and ratioEMAup<0.07: emojiema=('\U0001F4B0')*4
                            elif ratioEMAup>=0.07: emojiema=('\U0001F4B0')*5
                            if symbol == 'BTCUSDT':
                             fireemoji = '\U0001F389'*5
                             telegramal(chatid)
                            else:
                             telegramal(chatid)
                           def telegramalert(id,rat,icon,fng,fngval,iconfng):
                            hratioval = hr.read()
                            if float(hratioval)<0:iconhash='% \U0001F7E5'
                            elif float(hratioval)>0:iconhash='% \U0001F7E9'
                            bot.sendMessage(chat_id=id, text=icon+"#"+symbol + " has changed " + str("{0:.1%}".format(rat))+ " in 4 hours!"+icon+"\nLast Price: $"+str("{:.0f}".format(close[-2]))+"\nCurrent Price: $"+ str("{:.0f}".format(close[-1]))+"\nRSI: "+str("{:.2f}".format(rsivalue[-1]))+rsiicon+"\nBTC Dominance: "+str("{:.5}".format(dom.read()))+"\nHash Rate Change: "+str("{:.5}".format(hratioval))+iconhash+"\nFear&Greed Index: (Value: "+str(fngval)+", Status: "+fng+") "+iconfng+"\n\U000026D4Trailing StopLoss: $"+str("{:.0f}".format(sloss))+"\n\n"+candle)
                           if symbol == 'BTCUSDT':
                            ratio= (close[-1]-close[-2])/close[-2]
                            if rsivalue[-1] < 30:
                             rsiicon = ' \U0001F7E9'
                            elif rsivalue[-1] >=30 and rsivalue[-1] < 50:
                             rsiicon = ' \U0001F7E8'
                            elif rsivalue[-1] >=50 and rsivalue[-1] < 70:
                             rsiicon = ' \U0001F7E7'
                            elif rsivalue[-1] >=70:
                             rsiicon = ' \U0001F7E5'
                            doji = abs(open[-1] - close[-1])<=(high[-1]-low[-1])*0.05
                            BearishHarami = (close[-2] > open[-2]) and (open[-1] > close[-1]) and (open[-1] <= close[-2]) and (open[-2] <= close[-1]) and (open[-1] - close[-1] < close[-2] - open[-2])
                            BullishHarami = (open[-2] > close[-2]) and (close[-1] > open[-1]) and (close[-1] <= open[-2]) and (close[-2] <= open[-1]) and (close[-1] - open[-1] < open[-2] - close[-2])
                            BearishEngulfing = (close[-2] > open[-2]) and (open[-1] > close[-1]) and (open[-1] >= close[-2]) and (open[-2] >= close[-1]) and (open[-1] - close[-1] > close[-2] - open[-2] )
                            BullishEngulfing = (open[-2] > close[-2]) and (close[-1] > open[-1]) and (close[-1] >= open[-2]) and (close[-2] >= open[-1]) and (close[-1] - open[-1] > open[-2] - close[-2] )
                            EveningStar = (close[-3] > open[-3] and min(open[-2], close[-2]) > close[-3] and open[-1] < min(open[-2], close[-2]) and close[-1] < open[-1] )
                            MorningStar = (close[-3] < open[-3] and max(open[-2], close[-2]) < close[-3] and open[-1] > max(open[-2], close[-2]) and close[-1] > open[-1])
                            PiercingLine = (close[-2] < open[-2] and  open[-1] < low[-2] and close[-1] > (close[-2] + ((open[-2] - close[-2])/2)) and close[-1] < open[-2])
                            Hammer = (((high[-1] - low[-1])>3*(open[-1] -close[-1])) and  ((close[-1] - low[-1])/(.001 + high[-1] - low[-1]) > 0.6) and ((open[-1] - low[-1])/(.001 + high[-1] - low[-1]) > 0.6))
                            InvertedHammer = (((high[-1] - low[-1])>(3*(open[-1] -close[-1]))) and  ((high[-1] - close[-1])/(0.001 + high[-1] - low[-1]) > 0.6) and ((high[-1] - open[-1])/(0.001 + high[-1] - low[-1]) > 0.6))
                            #BullishBelt = (low[-1] == open[-1] and  open[-1] < lower and open[-1] < close[-1] and close[-1] > ((high[-2] - low[-2]) / 2) + low[-2])
                            BullishKicker = (open[-2]>close[-2] and open[-1]>=open[-2] and close[-1]>open[-1])
                            BearishKicker = (open[-2]<close[-2] and open[-1]<=open[-2] and close[-1]<=open[-1])
                            HangingMan = (((high[-1]-low[-1]>(4*(open[-1]-close[-1])))and((close[-1]-low[-1])/(0.001+high[-1]-low[-1])>=0.75)and((open[-1]-low[-1])/(0.001+high[-1]-low[-1])>=0.75)) and high[-2] < open[-1] and high[-3] < open[-1])
                            DarkCloudCover = ((close[-2]>open[-2])and(((close[-2]+open[-2])/2)>close[-1])and(open[-1]>close[-1])and(open[-1]>close[-2])and(close[-1]>open[-2])and((open[-1]-close[-1])/(.001+(high[-1]-low[-1]))>0.6))
                            candle=""
                            if doji:
                             candle = "\U0001F440 Formation: DOJI! \U0001F440"
#                            elif BullishHarami:
#                             candle = '\U0001F42E'+"Formation: BULLISH HARAMI!"+'\U0001F42E'
#                            elif BullishEngulfing:
#                             candle = '\U0001F42E'*3+"Formation: BULLISH ENGULFING!"+'\U0001F42E'*3
#                            elif BearishHarami:
#                             candle = '\U0001F43B'+"Formation: BEARISH HARAMI!"+'\U0001F43B'
#                            elif BearishEngulfing:
#                             candle = '\U0001F43B'*3+"Formation: BEARISH ENGULFING!"+'\U0001F43B'*3
                            elif EveningStar:
                             candle = '\U0001F43B'+"Formation: EVENING STAR!"+'\U0001F43B'
                            elif MorningStar:
                             candle = '\U0001F42E'+"Formation: MORNING STAR!"+'\U0001F42E'
                            elif PiercingLine:
                             candle = '\U0001F42E'+"Formation: PIERCING LINE!"+'\U0001F42E'
                            elif Hammer:
                             candle = '\U0001F42E'+'Formation: HAMMER!'+'\U0001F42E'
                            elif InvertedHammer:
                             candle = '\U0001F42E'+'Formation: INVERTED HAMMER!'+'\U0001F42E'
                            elif BullishKicker:
                             candle = '\U0001F42E'*2+'Formation: BULLISH KICKER!'+'\U0001F42E'*2
                            elif BearishKicker:
                             candle = '\U0001F43B'*2+'Formation: BEARISH KICKER!'+'\U0001F43B'*2
                            elif HangingMan:
                             candle = '\U0001F43B'+'Formation: HANGING MAN'+'\U0001F43B'*2
                            elif DarkCloudCover:
                             candle = '\U0001F43B'+'Formation: DARK CLOUD COVER!'+'\U0001F43B'
                            icon = ''
                            iconfng =''
                            if close[-1]>close[-2]: icon='\U0001F7E2'
                            elif close[-1]<close[-2]: icon='\U0001F534'
                            try:
                             url = 'https://api.alternative.me/fng/'
                             session = Session()
                             response = session.get(url)
                             datajson = json.loads(response.text)
                             fng = datajson['data'][0]['value_classification']
                             fngval = datajson['data'][0]['value']
                             if fng == 'Extreme Greed':iconfng = '\U0001F92E'
                             elif fng == 'Greed':iconfng = '\U0001F922'
                             elif fng == 'Neutral':iconfng = '\U0001F914'
                             elif fng == 'Fear':iconfng = '\U0001F628'
                             elif fng == 'Extreme Fear':iconfng = '\U0001F976'
                             print(fngval, fng)
                            except:print("FNG Problem")
                            telegramalert(chatid,ratio,icon,fng,fngval,iconfng)
                            if last_ema1 > last_ema2 and previous_ema1 < previous_ema2:telegramal(chatid)
                           count += 1
                        except: count+=1
                except Exception as exp:
                    print(exp.status_code, flush=True)
                    print(exp.message, flush=True)
            break
        except Exception as exp:
            print(exp.status_code, flush=True)
            print(exp.message, flush=True)
