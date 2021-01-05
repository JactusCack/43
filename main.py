import requests
from bs4 import BeautifulSoup
import cloudscraper
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import datetime
import random
import csv

from twocaptcha import TwoCaptcha
from setting import config
with requests.session() as r:
  with open('./profiles.csv') as csvfiles:
    reader = csv.DictReader(csvfiles)
    tasks_count = 1
    for row in reader:

      def time_format():
        now = str(datetime.datetime.now())
        now = now.split(' ')[1]
        now = '[' + str(now) + ']' + ' ' + '[43]'
        return now

        
      def random_proxy():
        global proxies_serv
        try:
          pl = open('proxies.txt').readlines()
          rp = random.choice(pl).strip()
          if len(rp.split(':')) == 2:
                        
            proxies_serv = {
                            'https': 'http://{}'.format(rp)
                            }
          elif len(rp.split(':')) == 4:
            splitted = rp.split(':')
            proxies_serv = {
                            'https': 'http://{0}:{1}@{2}:{3}'.format(splitted[2], splitted[3], splitted[0], splitted[1])
                            }
        except:
          proxies_serv = None
        return proxies_serv
      random_proxy()
      print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Proxy used : '+ str(proxies_serv))

      # cf handler 
      rq = cloudscraper.create_scraper(sess=r)

      #set bsid
      bsid = row['size']
      url = 'https://releases.43einhalb.com/raffle-form?productBsId=' + str(row['size'])

      def fetching_cookies():
        print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Selecting size...')
        global cooky
        rq.get(url)
        cooky = rq.cookies.get_dict()
        return cooky
      fetching_cookies()

      def captcha_solver():
        global gtoken
        api_key = config['2captcha']
        solver = TwoCaptcha(api_key)
        google_site_key = '6Ld7ha8UAAAAAF1XPgAtu53aId9_SMkVMmsK1hyK' 
        pageurl = 'https://releases.43einhalb.com/raffle-form?productBsId=505041' 
        rq.get(pageurl, proxies= proxies_serv)
        try:
          print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Solving captcha...')
          result = solver.recaptcha(sitekey=google_site_key, url=pageurl)
          gtoken = result['code']
          print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Captcha solved!')
        except:
          print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Error solving captcha, retrying...')
          captcha_solver()
      captcha_solver()
        
      def entering_form():
        usr = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                  'cokies' : str(cooky)
                }
        raffle_url = 'https://releases.43einhalb.com/enter-raffle'
        gett = rq.get(url, proxies= proxies_serv, headers= usr).text
        form_data = {
                      'productBsId': row['size'],
                      'salutation': row['gender'],
                      'firstName': row['firstname'],
                      'lastName': row['lastname'],
                      'email': row['email'],
                      'instagramName': row['insta'],
                      'street': row['adress'],
                      'streetNr': row['adressnumber'],
                      'zipCode' : row['postcode'],
                      'city': row['city'],
                      'country': row['country'],
                      'consent': 'Yes, I hereby accept the terms of participation. I confirm to receive emails from 43einhalb about this or similar products regularly. I agree with the privacy policy, which I can revoke any time at datenschutz@43einhalb.com}',
                      'gCaptchaToken' : gtoken
                  }
        try: 
          print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Entering raffle...')
          rq.post(raffle_url, data= form_data, headers= usr).text
          resp = rq.get(url, proxies= proxies_serv, headers= usr)
          if resp.status_code == 200 and "Aww yeah, you successfully  joined our raffle." in resp.text:
            print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'Succesfully entered!')
          else:
            print("Error submitting entry, error: {}".format(resp.status_code))
        except:
          print('error!')
      entering_form()

      def send_webhook():
        
        webhook = DiscordWebhook(url= str(config['webhook']))
        embed = DiscordEmbed(title='SUCCESFULL RAFFLE ENTRY', color=11403055)
        embed.add_embed_field(name='Website', value='43Einhalb')
        embed.add_embed_field(name='Email', value='||' + str(row['email']) + '||', inline= False)
        embed.add_embed_field(name='Proxies', value='||' + str(proxies_serv) + '||', inline= False)
        webhook.add_embed(embed)
        print(str(time_format()) + 'Tasks' + '[' + str(tasks_count) + ']' + '-----> ' + 'sent to webhook!')
        webhook.execute()
      send_webhook()
      tasks_count = tasks_count + 1

    print('stopping tasks')
    

                      

