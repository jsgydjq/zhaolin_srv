import re, base64
from HTMLParser import HTMLParser
from zhaolin.models import AppTable
from django.core.exceptions import ObjectDoesNotExist

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.app_name_cn = ''
        self.app_name_en = ''
        self.app_png_url = ''
        self.app_desc = ''
        self.app_detail_url = ''
        
        self.app_star = ''
        self.app_download_num = ''
        self.app_download_url = ''
        
        self.items = [] # save the result
        
        self.bydown = False
        self.start = False
        self.inner = False
        self.name_cn = False
        self.name_en = False
        self.down_num = False
        self.desc = False
        
    def get_items(self):
        return self.items
    
    def handle_starttag(self, tag, attrs):
        # handle start tag
        if tag=='div' and attrs:
            for key, value in attrs:
                if key=='id':
                    if value=='bydown':
                        self.bydown = True
                        return
                        
                if self.bydown==True and key=='class' and value=='app_section':
                    self.start = True
                    return
                if self.bydown==True and key=='class' and value=='star-off fl':
                    self.inner = True
                    return
                    
        if self.start==True:
            if tag=='img' and attrs:
                for key, value in attrs:
                    if key=='class' and value=='app_icon':
                        for _key, _value in attrs:
                            if _key=='src':
                                self.app_png_url = _value
                                return
                    
            if tag=='p' and attrs:
                for key, value in attrs:
                    if key=='class' and value=='app_name ch':
                        self.name_cn = True
                        return
                    if key=='class' and value=='app_name en':
                        self.name_en = True
                        return
                    if key=='class' and value=='app_info':
                        self.down_num = True
                        return
                    if key=='class' and value=='app_info desc':
                        self.desc = True
                        return

            if tag=='a' and attrs:
                for key, value in attrs:
                    if key=='class' and value=='detail_app':
                        for _key, _value in attrs:
                            if _key=='href':
                                self.app_detail_url = 'http://www.appchina.com' + _value
                                return
                    if key=='class' and value=='download_app':
                        for _key, _value in attrs:
                            if _key=='href':
                                self.app_download_url = _value
                                return

            if self.inner==True and tag=='input' and attrs:
                for key, value in attrs:
                    if key=='value':
                        self.app_star = float(value)
                        return
            
            
    def handle_data(self, data):
        if self.name_cn == True:
            self.app_name_cn = data
            return
            
        if self.name_en == True:
            self.app_name_en = data
            return
        
        if self.down_num == True:
            self.app_download_num = int(re.findall(r'[\d]+', data)[0])
            self.down_num = False
            return
        
        if self.desc == True:
            self.app_desc = data
            return
            
    def handle_endtag(self, tag):
        if self.start==True and tag=='p':
            if self.name_cn==True:
                self.name_cn = False
                return
            if self.name_en==True:
                self.name_en = False
                return
            if self.down_num==True:
                self.down_num = False
                return
            if self.desc==True:
                self.desc = False
                return
        if self.start==True and tag=='div':
            if self.inner==True:
                self.inner = False
                return
            else:
                self.start = False
                self.items.append((self.app_name_cn, self.app_name_en, self.app_png_url, self.app_desc, self.app_detail_url, self.app_star, self.app_download_num, self.app_download_url))
                return
        if self.bydown==True and tag=='div':
            self.bydown = False
            return

def analyze(content):
    #print content
    parser = MyHTMLParser()
    parser.feed(content)
    items = parser.get_items()
    for item in items:
        #print base64.encodestring(item[0].encode('utf-8'))

        try:
            temp = AppTable.objects.get(name_cn=base64.encodestring(item[0].encode('utf-8')))
        except ObjectDoesNotExist:
            AppTable.objects.create(name_cn=base64.encodestring(item[0].encode('utf-8')), name_en=item[1], icon_url=item[2], descript=base64.encodestring(item[3].encode('utf-8')), detail_url=item[4], star_rate=item[5], down_count=item[6], down_url=item[7]) 

