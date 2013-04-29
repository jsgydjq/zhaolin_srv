import re, base64
from HTMLParser import HTMLParser
from zhaolin.models import AppInfo
from django.core.exceptions import ObjectDoesNotExist

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.app_name_cn = ''
        self.app_name_en = ''
        self.app_png_url = ''
        self.app_desc = ''
        self.app_detail_url = ''
        
        self.app_star = 0.0
        self.app_download_num = 0
        self.app_download_url = ''
        
        self.items = [] # save the result
        
        self.start = False
        self.icon = False
        self.info = False
        self.top = False
        self.down = False
        self.desc = False
        self.downnum = False

    def get_items(self):
        return self.items
    
    def handle_starttag(self, tag, attrs):
        # handle start tag
        if tag=='div' and attrs:
            for key, value in attrs:
                if key=='class' and value=='app_list border_three':
                    self.start = True
                    return
                if key=='class' and value=='app_icon':
                    self.icon = True
                    return
                if key=='class' and value=='app_info':
                    self.info = True
                    return
                if key=='class' and value=='app_top':
                    self.top = True
                    return
                if key=='class' and value=='app_down':
                    self.down = True
                    return
                    
        if self.start==True:
            if tag=='span' and attrs:
                for key, value in attrs:
                    if key=='class' and value=='app_downnum l':
                        self.downnum = True
                        return
                    if key=='class' and value=='stars center':
                        for _key, _value in attrs:
                            if _key=='style':
                                num = float(re.findall(r'([\d]+)px', _value)[0])
                                self.app_star = round(float(num)/24, 1)
                                return

            if self.icon==True:
                if tag=='a' and attrs:
                    for key, value in attrs:
                        if key=='title':
                            self.app_name_cn = value
                        if key=='href':
                            self.app_detail_url = 'http://www.anzhi.com' + value
                    return
                if tag=='img' and attrs:
                    for key, value in attrs:
                        if key=='src':
                            self.app_png_url = value
                            return
            if self.down==True:
                if tag=='a' and attrs:
                    for key, value in attrs:
                        if key=='onclick':
                            app_id = re.findall(r'[\d]+', value)[0]
                            self.app_download_url = 'http://www.anzhi.com/dl_app.php?s=' + app_id + '&n=5'
                            return                               
                               
            if self.info==True and tag=='p':
                self.desc = True

    def handle_data(self, data):
        if self.downnum==True:
            self.app_download_num = get_num(data) 
            return
            
        if self.desc==True:
            self.app_desc = data
            return

    def handle_endtag(self, tag):
        if self.start==True and tag=='div':
            if self.icon==True:
                self.icon = False
                return
            if self.top==True:
                self.top = False
                return
            if self.info==True:
                self.info = False
                return
            if self.down==True:
                self.down = False
                return
            if self.start==True:
                self.start = False
                return

        if self.start==True and tag=='span':
            if self.downnum==True:
                self.downnum = False
                return

        if self.start==True and tag=='p':
            if self.desc==True:
                self.desc = False
                return
        
        if self.start==True and tag=='li':
            self.items.append((self.app_name_cn, self.app_name_en, self.app_png_url, self.app_desc, self.app_detail_url, self.app_star, self.app_download_num, self.app_download_url))

def analyze(content):
    #print content
    parser = MyHTMLParser()
    parser.feed(content)
    items = parser.get_items()
    for item in items:
        try:
            temp = AppInfo.objects.get(appname=base64.encodestring(item[0].encode('utf-8')))
            if temp.from_user==True:
                temp.app_type = 1
                temp.from_user = False
                temp.icon_url = item[2]
                temp.descript = base64.encodestring(item[3].encode('utf-8'))
                temp.detail_url = item[4]
                temp.star_rate = item[5]
                temp.down_count = item[6]
                temp.down_url = item[7]
                temp.save()

        except ObjectDoesNotExist:
            AppInfo.objects.create(appname=base64.encodestring(item[0].encode('utf-8')), icon_url=item[2], descript=base64.encodestring(item[3].encode('utf-8')), detail_url=item[4], star_rate=item[5], down_count=item[6], down_url=item[7], app_type=1, from_user=False) 

def get_num(rawData):
    num_unit = re.findall(u'([\d]+)([\u4e07|\u5343]?)', rawData)[0]
    num = int(num_unit[0])
    unit = num_unit[1]
    if unit==u'\u4e07': # 10,000
        num = num * 10000
    elif unit==u'\u5343': # 1,000
        num = num * 1000
    return num
