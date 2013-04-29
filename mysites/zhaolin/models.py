from django.db import models
ICONURLROOT = 'http://zhaolin.iseeqit.com/media/appIcon/' # TODO

class UserInfo(models.Model):
    username = models.CharField(max_length=64, blank=True)
    headUrl = models.CharField(max_length=256, blank=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    mobileModel = models.CharField(max_length=32, blank=True)
    btMac = models.CharField(max_length=64, blank=True)
    wlMac = models.CharField(max_length=64, blank=True)
    IMEI = models.CharField(max_length=32, blank=True)

    renrenId = models.CharField(max_length=16, blank=True)
    weiboId = models.CharField(max_length=16, blank=True)
    tencentId = models.CharField(max_length=16, blank=True)
    weixinId = models.CharField(max_length=32, blank=True)

    def __unicode__(self):
        return self.renrenId

class Collect(models.Model):
    userInfo = models.OneToOneField(UserInfo)

class AppInfo(models.Model):
    appname = models.CharField(max_length=128, primary_key=True)
    icon_url = models.CharField(max_length=256, blank=True)
    descript = models.CharField(max_length=512, blank=True)
    detail_url = models.CharField(max_length=256, blank=True)
    down_url = models.CharField(max_length=256, blank=True)
    star_rate = models.FloatField(default=0)
    down_count = models.BigIntegerField(default=0)
    apk_size = models.FloatField(default=0) # in terms of MB

    users = models.ManyToManyField(UserInfo)
    collectors = models.ManyToManyField(Collect)
    # -1: Unknown, 0: Game, 1: Tools, ...
    app_type = models.IntegerField(default=-1)
    from_user = models.BooleanField(default=False)

    def get_icon_url(self):
        if self.icon_url.startswith('http'):
            return self.icon_url
        else:
            return ICONURLROOT + self.icon_url

    def get_down_url(self):
        return self.down_url

    def get_apk_size(self):
        return self.apk_size
    def __unicode__(self):
        return self.appname

'''
class AppInfo(models.Model):
    APPNAME = models.CharField(max_length=128)
    ICON = models.ImageField(blank=True, null=True, upload_to='appIcon/')
    SIZE = models.BigIntegerField(default=-1)
    VERSION = models.CharField(max_length=64)
    USER = models.ForeignKey(UserInfo)

    def __unicode__(self):
        return self.APPNAME
'''
