# encoding=utf-8
import os
import re
from bs4 import BeautifulSoup as bs
import json
import sys
import imghdr
import random
import datetime
import difflib
import shutil
import smtplib
from email.mime.text import MIMEText
from email.header import Header
PY3 = sys.version.startswith('3')
if PY3:
    from urllib.request import Request, urlopen
    print ('python 3')
else:
    from urllib2 import Request, urlopen
    print ('python 2')

reload(sys)
sys.setdefaultencoding('utf8')

class Crawler(object):
    def __init__(self):
        super(Crawler, self).__init__()
        self.links = []
        self.ids= []
        self.names= []
    

    def readRootJSON(self, html):
        req = Request(html)
        resp = urlopen(req)
        content = resp.readline()
        for page in range(1, 122):
            content = resp.readline()
        if PY3:
            charset = resp.headers.get_content_charset()
        else:
            charset = resp.headers.getparam('charset')
        if charset:
            content = content.decode(charset)
        return content

    def readContent(self, html):
        req = Request(html)
        resp = urlopen(req)
        content = resp.read()
        if PY3:
            charset = resp.headers.get_content_charset()
        else:
            charset = resp.headers.getparam('charset')
        if charset:
            content = content.decode(charset)

        soup = bs(content, 'html.parser')
        albums = soup.find_all('script', id = 'content_tpl')
        return albums

    def getLinkIdAndNames(self, htmlData):
        htmlData = htmlData[19:]
        json_to_python = json.loads(htmlData)
        for index1, item1 in enumerate(json_to_python["list"]):
            if len(item1["children"])>0:
                for index2, item2 in enumerate(item1["children"]):
                    if len(item2["children"])>0:
                        for index3, item3 in enumerate(item2["children"]):
                            self.ids.append(item3["id"])
                            self.names.append(item3["name"])
                    else:
                        self.ids.append(item2["id"])
                        self.names.append(item2["name"])
            else:
                self.ids.append(item1["id"])
                self.names.append(item1["name"])

    def getContent(self):
        if os.path.exists('HTML'):
            dirname = datetime.datetime.now().strftime('%Y-%m-%d')
            try:
                os.mkdir(dirname)
            except OSError as e:
                pass
            os.chdir(dirname)
            length = 0
            for index, model_id in enumerate(self.ids):
                filename = self.names[index]+'_'+model_id+'.html'
                test_html = 'https://mp.weixin.qq.com/wiki?action=doc&id={0}&t={1}'
                d = Crawler()
                print ('start downloading %s %s' %(self.names[index], model_id))
                contents = d.readContent(test_html.format(model_id, random.random()))
                for i, content in enumerate(contents):
                    with open(filename, 'wb') as img:
                        img.write(content.prettify()[42:-10])
                os.chdir('..')
                os.chdir('HTML')
                fromlines = open(filename, 'U').read().decode()
                os.chdir('../'+dirname)
                tolines = open(filename, 'U').read().decode()
                print ('start diff %s %s' %(self.names[index], model_id))
                count = len(list(difflib.unified_diff(fromlines, tolines, fromfile='HTML', tofile=dirname)))
                if count>0:
                    length += 1
                    os.chdir('..')
                    with open(self.names[index]+'_'+model_id+'.txt', 'wb') as img:
                        for line in difflib.unified_diff(fromlines, tolines, fromfile='HTML', tofile=dirname):
                            img.write(line+"\n")
                    os.chdir('HTML')
                    with open(filename, 'wb') as img:
                        img.write(content.prettify()[42:-10])
                    os.chdir('../'+dirname)
            os.chdir('..')
            shutil.rmtree(dirname)  
            print ('totall diff %s docs' %(length))
        else:
            try:
                os.mkdir('HTML')
            except OSError as e:
                pass
            os.chdir('HTML')
            for index, model_id in enumerate(self.ids):
                test_html = 'https://mp.weixin.qq.com/wiki?action=doc&id={0}&t={1}'
                filename = self.names[index]+'_'+model_id+'.html'
                d = Crawler()
                print ('start downloading %s %s' %(model_id, self.names[index]))
                contents = d.readContent(test_html.format(model_id, random.random()))
                for i, content in enumerate(contents):
                    with open(filename, 'wb') as img:
                        img.write(content.prettify()[42:-10])

if __name__ == '__main__':
    test_html = 'https://mp.weixin.qq.com/wiki'
    c = Crawler()
    data = c.readRootJSON(test_html)
    c.getLinkIdAndNames(data)
    c.getContent()