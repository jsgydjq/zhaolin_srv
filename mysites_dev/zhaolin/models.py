from django.db import models
import time
import base64

ICONURLROOT = 'http://testzl.iseeqit.com/media/appIcon/' # TODO

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

    def getUserInfo(self):
        user_info = {}
        user_info['userPrimkey'] = self.pk
        user_info['userName'] = base64.b64decode(self.username)
        user_info['headUrl'] = self.headUrl
        try:
            user_info['status'] = base64.b64decode(self.status.order_by('-timestamp')[0])
        except:
            pass
        user_info['mobileModel'] = self.mobileModel
        user_info['collectCount'] = self.externalInfo.collectCount
        return user_info

    def follow(self, followee):
        try:
            followInfo = self.followInfo
        except:
            followInfo = FollowInfo.objects.create(user=self)
        try:
            followInfo.followed.get(pk=followee.pk)
            already=True
        except:
            already=False
        if not already:
            followInfo.followed.add(followee)
            followInfo.save()
            return True
        return False

    def disfollow(self, followee):
        try:
            followInfo = self.followInfo
        except:
            followInfo = FollowInfo.objects.create(user=self)
        try:
            followInfo.followed.get(pk=followee.pk)
            already=True
        except:
            already=False
        if already:
            followInfo.followed.remove(followee)
            followInfo.save()
            return True
        return False


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
    from_user = models.BooleanField(default=True)

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

    def getAppInfo(self):
        app_info = {}
        app_info['appname']=base64.b64decode(self.appname)
        app_info['icon_url']=self.get_icon_url()
        app_info['down_url']=self.get_down_url()
        try:
            self.externalappinfo
        except:
            ExternalAppInfo.objects.create(app=self)
        app_info['down_count'] = self.down_count
        app_info['rateRank'] = self.star_rate
        try:
            commentCount = self.relatedActions.count()
        except:
            commentCount = 0
        app_info['commentCount'] = commentCount
        try:
            action = self.relatedActions.order_by('-upCount')[0]
            action.ctCount = 1
            action.save()
            '''
            try:
                self.collected.action.ctCount = 0
                self.collected.action.save()
                self.collected.save()
                self.collected.action = action
                self.collected.save()
            except:
                CollectedAction.objects.create(app = self, action = action)
            '''

            user_descript = base64.b64decode(action.comment)
        except:
            user_descript = 'No user generated description yet'
            
        app_info['user_descript'] = user_descript
        app_info['upCount']=self.externalappinfo.upCount
        app_info['downCount']=self.externalappinfo.downCount
        app_info['userCount']=self.users.count()
        return app_info

    def getCommentList(self):
        commentList = self.relatedActions.values_list('comment', 'externalactioninfo__commentType')
        result = []
        for comment in commentList:
            item = {}
            item['content'] = base64.b64decode(comment[0])
            item['type'] = comment[1]
            result.append(item)
        return result

# action_kind:
#   -1: Empty
#    0: Install|Share
#    1: Collect
class User_Action(models.Model):
    user = models.ForeignKey(UserInfo)
    appname = models.CharField(max_length=128, blank=True)
    action_kind = models.IntegerField(default=-1)
    timestamp = models.DateTimeField(auto_now=True)

class Action_Comment(models.Model):
    action = models.ForeignKey(User_Action)
    user = models.ForeignKey(UserInfo)
    comment = models.CharField(max_length=512, blank=True)
    up_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

class NewActionDetail(models.Model):
    initiator = models.ForeignKey(UserInfo, related_name='myActions')
    app = models.ForeignKey(AppInfo, related_name='relatedActions')
    actionType = models.IntegerField(default=-1)
    comment = models.CharField(max_length=512, blank=True)
    upCount = models.IntegerField(default=0)
    downCount = models.IntegerField(default=0)
    ctCount = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def getCommentList(self):
        comments = []
        for comment in self.commentList.order_by('-timestamp'):
            comments.append(comment.getCommentInfo())
        return comments

    def getActionBrief(self):
        actionDetail = {}
        actionDetail['primKey'] = self.pk
        actionDetail['userInfo'] = self.initiator.getUserInfo()
        actionDetail['appInfo'] = self.app.getAppInfo()
        actionDetail['actionType'] = self.externalactioninfo.commentType#self.actionType
        actionDetail['comment'] = base64.b64decode(self.comment)
        actionDetail['upCount'] = self.upCount
        actionDetail['downCount'] = self.downCount
        actionDetail['timestamp'] = str(int(time.mktime(self.timestamp.timetuple()) * 1000))
        return actionDetail

class ExternalActionInfo(models.Model):
    action = models.OneToOneField(NewActionDetail)
    commentType = models.IntegerField(default=0) #-1:negative,0:default, 1:positive

class NewActionComment(models.Model):
    action = models.ForeignKey(NewActionDetail, related_name='commentList')
    poster = models.ForeignKey(UserInfo, related_name='postedActionComments')
    receiver = models.ForeignKey(UserInfo, related_name='receivedActionComments')
    content = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def getCommentInfo(self):
       comment = {}
       comment['primKey'] = self.pk
       comment['poster'] = self.poster.getUserInfo()
       comment['receiver'] = self.receiver.getUserInfo()
       comment['content'] = self.content
       comment['timestamp'] = str(int(time.mktime(self.timestamp.timetuple()) * 1000))
       return comment

class ExternalAppInfo(models.Model):
    app = models.OneToOneField(AppInfo)
    upCount = models.IntegerField(default=0)
    downCount = models.IntegerField(default=0)
    ctCount = models.IntegerField(default=0)

class NewUserStatus(models.Model):
    user = models.ForeignKey(UserInfo, related_name='status')
    content = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
     
    def getStatusBrief(self):
        actionDetail = {}
        actionDetail['primKey'] = self.p
        actionDetail['content'] = self.content
        actionDetail['timestamp'] = str(int(time.mktime(self.timestamp.timetuple()) * 1000))
        return actionDetail

    def getMessageList(self):
        messages = []
        for message in self.replies.order_by('-timestamp'):
            messages.append(message.getMessageInfo())
        return messages

class NewMessage(models.Model):
    user = models.ForeignKey(UserInfo, related_name='messages')
    userstatus = models.ForeignKey(NewUserStatus, blank=True, null=True, related_name='replies')
    poster = models.ForeignKey(UserInfo, related_name='postedMessages')
    receiver = models.ForeignKey(UserInfo, related_name='receivedMessages')
    content = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def getMessageInfo(self):
       message = {}
       message['primKey'] = self.pk
       message['poster'] = self.poster.getUserInfo()
       message['receiver'] = self.receiver.getUserInfo()
       message['content'] = self.content
       message['timestamp'] = str(int(time.mktime(self.timestamp.timetuple()) * 1000))
       return message

class FollowInfo(models.Model):
    user = models.OneToOneField(UserInfo, related_name='followInfo')
    followed = models.ManyToManyField(UserInfo, related_name='followers')
    
class ExternalUserInfo(models.Model):
    user = models.OneToOneField(UserInfo, related_name='externalInfo')
    collectCount = models.IntegerField(default=0)

    def updateCollectCount(self):
        self.collectCount = self.user.myActions.filter(ctCount=1).count()
        self.save()

class CollectedAction(models.Model):
    app = models.OneToOneField(AppInfo, related_name='collected')
    action = models.OneToOneField(NewActionDetail, related_name='collect_app')
