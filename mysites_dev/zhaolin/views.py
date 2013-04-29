import logging
logger = logging.getLogger('zhaolin_debug')

import base64, hashlib

from zhaolin.models import *
from zhaolin import position

from django.http import HttpResponse
from django.utils import simplejson
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

def update_user(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            logger.debug('user info posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            renrenId = req.get('renrenId')
            userName = req.get('userName')
            try:
                user = UserInfo.objects.get(renrenId = renrenId)
                user.username = userName
            except:
                user = UserInfo.objects.create(renrenId = renrenId,
                                               username = userName)
                Collect.objects.create(userInfo = user)
                ExternalUserInfo.objects.create(user = user)

            location = req.get('location', '0,0').split(',')

            latitude = float(location[0])
            longitude = float(location[1])

            mobileModel = req.get('mobileModel', 'NULL')
            headUrl = req.get('headUrl', 'NULL')
            btMac = req.get('btmac', 'NULL')
            wlMac = req.get('wlmac', 'NULL')
            IMEI = req.get('IMEI', 'NULL')

            user.headUrl = headUrl
            user.latitude = latitude
            user.longitude = longitude
            user.mobileModel = mobileModel
            user.btMac = btMac
            user.wlMac = wlMac
            user.IMEI = IMEI
            user.save()
            response['userPrimkey'] = user.pk
            response['result'] = 0
    except:
        response['result'] = 1

    json = simplejson.dumps(response)
    logger.debug('response to update: ' + json)
    return HttpResponse(json)

def update_location(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            logger.debug('update location, posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            primkey = req.get('primkey')
            try:
                user = UserInfo.objects.get(pk = primkey)
            except:
                json = simplejson.dumps(response)
                return HttpResponse(json)

            location = req.get('location', '0,0').split(',')

            latitude = float(location[0])
            longitude = float(location[1])

            user.latitude = latitude
            user.longitude = longitude
            user.save()

            friend_renrenIds = req.get('friendidList').split(',')
            friend_renrenIds = set(friend_renrenIds)

            exist_renrenIds = UserInfo.objects.values_list('renrenId', flat=True)
            exist_renrenIds = set(exist_renrenIds)

            valid_renrenIds = exist_renrenIds & friend_renrenIds

            # TODO validate
            friends = UserInfo.objects.filter(renrenId__in=list(valid_renrenIds))

            try:
                userFollowInfo = user.followInfo
            except:
                userFollowInfo = FollowInfo.objects.create(user=user)

            for friend in friends:
                try:
                    FollowInfo = friend.followInfo
                except:
                    FollowInfo = FollowInfo.objects.create(user=friend)
                try:
                    userFollowInfo.followed.get(pk=followee.pk)
                    already = True
                except:
                    already = False
                
            response['result'] = 0
    except:
        response['result'] = 1

    json = simplejson.dumps(response)
    return HttpResponse(json)

def share_apps(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            #logger.debug('Share apps, posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            primkey = req.get('primkey')
            try:
                user = UserInfo.objects.get(pk = primkey)
            except:
                return HttpResponse(simplejson.dumps(response))

            appList = req.get('appList', None)

            exist_app_names = AppInfo.objects.values_list('appname',
                                                            flat=True)
            exist_app_names = set(exist_app_names)
            shared_app_names = user.appinfo_set.values_list('appname',
                                                            flat=True)
            shared_app_names = set(shared_app_names)

            for item in appList:
                action = User_Action(appname=item['name'],action_kind = 0,user = user)
                action.save()
                if item['name'] not in exist_app_names:
                    #logger.debug('app item'+simplejson.dumps(app_item))
                    app_item = AppInfo(appname=item['name'],
                                        apk_size=long(item['size']),
                                        from_user=True)
                    feed = item['name']
                    md5obj = hashlib.md5(feed.encode('utf-8'))
                    fileName = md5obj.hexdigest() + ".png"
                    file = open('./media/appIcon/'+fileName, 'wb')
                    file.write(base64.b64decode(item['img']))
                    file.close()

                    app_item.icon_url = fileName
                    app_item.save()
                    app_item.users.add(user)
                elif item['name'] not in shared_app_names:
                    try:
                        app_item = AppInfo.objects.get(appname=item['name'])
                    except:
                        return HttpResponse(simplejson.dumps(response))

                    app_item.users.add(user)
                else:
                    pass
            response['result'] = 0
    except:
        response['result'] = 1

    return HttpResponse(simplejson.dumps(response))

def collect_app(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            logger.debug('collect action, posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            primkey = req.get('primkey', '0')
            appName = req.get('appName', '0')
            bCollect = request.GET('bCollect', True)

            try:
                user = UserInfo.objects.get(pk = primkey)
            except:
                return HttpResponse(simplejson.dumps(response))

            try:
                app_item = AppInfo.objects.get(appname = appName)
            except:
                return HttpResponse(simplejson.dumps(response))

            try:
                if bCollect:
                    user.collect.appinfo_set.add(app_item)
                else:
                    user.collect.appinfo_set.remove(app_item)
            except:
                return HttpResponse(simplejson.dumps(response))
            response['result'] = 0

    except:
        response['result'] = 1

    return HttpResponse(simplejson.dumps(response))

def get_friend_apps(request):
    response = {}
    response['result'] = -1
    app_dict = {}
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug('get friend apps, post: '+ request.raw_post_data)
            friend_renrenIds = req.get('friendidList').split(',')
            friend_renrenIds = set(friend_renrenIds)

            exist_renrenIds = UserInfo.objects.values_list('renrenId', flat=True)
            exist_renrenIds = set(exist_renrenIds)

            valid_renrenIds = exist_renrenIds & friend_renrenIds

            # TODO validate
            friends = UserInfo.objects.filter(renrenId__in=list(valid_renrenIds))
            logger.debug('friend count: %s', friends.count())
            for friend in friends:
                apps = friend.appinfo_set.all()
                for app_item in apps:
                    if app_item.appname not in app_dict:
                        app_info = {}
                        app_info['appname'] = app_item.appname
                        app_info['count'] = 1
                        app_info['icon_url'] = app_item.get_icon_url()
                        app_info['size'] = app_item.get_apk_size()
                        app_info['distance'] = 0
                        app_info['down_url'] = app_item.get_down_url()
                        app_info['users'] = []
                        app_dict[app_item.appname] = app_info
                    else:
                        app_info = app_dict[app_item.appname]
                        app_info['count'] += 1
                    user_info = friend.getUserInfo()
                    app_dict[app_item.appname]['users'].append(user_info)
            response['result'] = 0
    except:
        response['result'] = 1

    app_list = app_dict.values()
    paginator = Paginator(app_list, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    response['appList'] = resp
    json = simplejson.dumps(response)
    #logger.debug('response to get friend apps: page  '+page + ': ' + json)
    return HttpResponse(json)

def get_nearby_apps(request):
    response = {}
    response['result'] = -1
    app_dict = {}
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            logger.debug("Get nearby, post: " + request.raw_post_data)
            location = req.get('location', '0,0').split(',')
            longitude = float(location[1])
            latitude = float(location[0])

            delta_long = position.change_in_longitude(latitude, 1)
            delta_lati = position.change_in_latitude(1)
            max_lati = latitude + delta_lati
            min_lati = latitude - delta_lati
            max_long = longitude + delta_long
            min_long = longitude - delta_lati

            nearby_users = UserInfo.objects.filter(
                longitude__lte=max_long, longitude__gte=min_long,
                latitude__lte=max_lati, latitude__gte=min_lati)

            #tmp_user = UserInfo.objects.get(renrenId = '261843626')
            #nearby_users.append(tmp_user)

            for user in nearby_users:
                distance = position.get_distance(longitude, latitude,
                                        user.longitude, user.latitude)
                apps = user.appinfo_set.all()
                for app_item in apps:
                    if app_item.appname not in app_dict:
                        app_info = {}
                        app_info['appname'] = app_item.appname
                        app_info['count'] = 1
                        app_info['icon_url'] = app_item.get_icon_url()
                        app_info['size'] = app_item.get_apk_size()
                        app_info['distance'] = distance
                        app_info['down_url'] = app_item.get_down_url()
                        app_info['users'] = []
                        app_dict[app_item.appname] = app_info
                    else:
                        app_info = app_dict[app_item.appname]
                        app_info['count'] += 1
                        if app_info['distance'] > distance:
                            app_info['distance'] = distance
                    user_info = user.getUserInfo()
                    app_dict[app_item.appname]['users'].append(user_info)
            response['result'] = 0
    except:
        response['result'] = 1

    app_list = app_dict.values()
    paginator = Paginator(app_list, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    response['appList'] = resp
    json = simplejson.dumps(response)
    #logger.debug('response to get nearby: ' + json)
    return HttpResponse(json)

def get_friend_list(request):
    response = {}
    response['result'] = -1
    friend_list = []
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug('get friend list, posted: '+ request.raw_post_data)
            friend_renrenIds = req.get('friendidList').split(',')
            friend_renrenIds = set(friend_renrenIds)

            exist_renrenIds = UserInfo.objects.values_list('renrenId', flat=True)
            exist_renrenIds = set(exist_renrenIds)

            valid_renrenIds = exist_renrenIds & friend_renrenIds

            friends = UserInfo.objects.filter(renrenId__in=list(valid_renrenIds))
            for friend in friends:
                user_info = friend.getUserInfo()
                user_info['newsCount'] = friend.user_action_set.count()
                friend_list.append(user_info)
            response['result'] = 0
    except:
        response['result'] = 1

    app_list = friend_list
    paginator = Paginator(app_list, 20)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    response['appList'] = resp
    json = simplejson.dumps(response)
    return HttpResponse(json)

def get_user_detail(request):
    response = {}
    response['result'] = -1
    response['userDetail'] = ''
    try:
        if request.method == 'POST':
            #logger.debug('get friend list, posted: '+ request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            primkey = req.get('primkey')
            try:
                user = UserInfo.objects.get(pk = primkey)
            except:
                return HttpResponse(simplejson.dumps(response))
            user_info = getUserDetail(primkey)
            response['userDetail'] = user_info
            response['result'] = 0
    except:
        response['result'] = 1
    json = simplejson.dumps(response)
    return HttpResponse(json)

def get_nearby_people(request):
    response = {}
    response['result'] = -1
    user_list = []
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug("Get nearby people, post: " + request.raw_post_data)
            location = req.get('location', '0,0').split(',')
            longitude = float(location[1])
            latitude = float(location[0])

            delta_long = position.change_in_longitude(latitude, 1)
            delta_lati = position.change_in_latitude(1)
            max_lati = latitude + delta_lati
            min_lati = latitude - delta_lati
            max_long = longitude + delta_long
            min_long = longitude - delta_lati

            nearby_users = UserInfo.objects.filter(
                longitude__lte=max_long, longitude__gte=min_long,
                latitude__lte=max_lati, latitude__gte=min_lati)

            for user in nearby_users:
                distance = position.get_distance(longitude, latitude,
                                        user.longitude, user.latitude)
                user_info = user.getUserInfo()
                user_info['distance'] = distance
                action_list = []
                try:
                    actions = user.myActions.order_by('-timestamp')[:3]
                    for action in actions:
                        action_list.append(action.getActionBrief())
                except:
                    pass
                item = {}
                item['userInfo'] = user_info
                item['actionList'] = action_list

                user_list.append(item)
            response['result'] = 0
    except:
        response['result'] = 1

    paginator = Paginator(user_list, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    response['userList'] = resp
    json = simplejson.dumps(response)
    #logger.debug('response to get nearby: ' + json)
    return HttpResponse(json)
    
def getUserDetail(primkey, top_k = 10):
    try:
        user = UserInfo.objects.get(pk = primkey)
    except:
        return user_info
    user_info=user.getUserInfo()
    user_info['appList'] = []
    user_info['actionList'] = []
    app_names = user.appinfo_set.values_list('appname',flat=True)
    for name in app_names:
        app_info = getAppDetail(name)
        user_info['appList'].append(app_info)

    actions = user.user_action_set.order_by('-timestamp')[:top_k]
    for action in actions:
        action_item = {}
        action_item['appInfo'] = getAppDetail(action.appname)
        action_item['actionType'] = action.action_kind
        user_info['actionList'].append(action_item)

    return user_info

def getAppDetail(app_name):
    try:
        app_item = AppInfo.objects.get(appname=app_name)
    except:
        return app_info
    app_info = app_item.getAppInfo()
    app_info['count'] = 0
    app_info['size'] = 0.0
    app_info['distance'] = 20.0
    app_info['users'] = []

    app_info['count'] = app_item.users.count()
    app_info['size'] = app_item.get_apk_size()
    users = app_item.users.all()
    for friend in users:
        user_info = friend.getUserInfo()
        app_info['users'].append(user_info)

    return app_info

def post_follow_one(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            flerPrimKey = req.get('flerPrimKey', -1)
            fleePrimKey = req.get('fleePrimKey', -1)
            logger.debug('1')
            try:
                follower = UserInfo.objects.get(pk=flerPrimKey)
                followee = UserInfo.objects.get(pk=fleePrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            try:
                followInfo = follower.followInfo
            except:
                logger.debug('6')
                followInfo = FollowInfo.objects.create(user=follower)
                logger.debug('7')
            try:
                followInfo.followed.get(pk=followee.pk)
                already = True
            except:
                already = False

            if already:
                logger.debug('2')
                followInfo.followed.remove(followee)

                logger.debug('3')
            else:
                logger.debug('4')
                followInfo.followed.add(followee)
                logger.debug('5')
            response['result'] = 0
    except:
        response['result'] = 1
    return HttpResponse(simplejson.dumps(response))

def post_new_action(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            logger.debug("Post new action, post: " + request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            userPrimKey = req.get('userPrimKey', -1)
            appName = req.get('appName', 'null')
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
                app = AppInfo.objects.get(appname=appName)
            except:
                return HttpResponse(simplejson.dumps(response))
            actionType = req.get('actionType', -1)
            comment = req.get('comment', '')

            action = NewActionDetail.objects.create(initiator=user, app=app,
                                                    actionType=actionType,
                                                    comment=comment)
            response['result'] = 0
    except:
        response['result'] = 1
    return HttpResponse(simplejson.dumps(response))

def post_new_status(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug("Post new status, post: " + request.raw_post_data)
            userPrimKey = req.get('userPrimKey', -1)
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            content = req.get('content', '')
            status = NewUserStatus.objects.create(user=user,content=content)
            response['result'] = 0
    except:
        response['result'] = 1
    return HttpResponse(simplejson.dumps(response))

def post_new_message(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            userPrimKey = req.get('userPrimKey', -1)
            statPrimKey = req.get('statPrimKey', -1)
            postPrimKey = req.get('postPrimKey', -1)
            recvPrimKey = req.get('recvPrimKey', -1)
            content = req.get('content', '')
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
                poster = UserInfo.objects.get(pk=postPrimKey)
                receiver = UserInfo.objects.get(pk=recvPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            try:
                status = NewUserStatus.objects.get(pk=statPrimKey)
                NewMessage.objects.create(user=user, userstatus = status,
                                        poster=poster, receiver=receiver,
                                        content = content)
            except:
                NewMessage.objects.create(user=user, content = content,
                                        poster=poster, receiver=receiver)
                                        

            response['result'] = 0
    except:
        response['result'] = 1
    return HttpResponse(simplejson.dumps(response))

def post_new_comment(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            actiPrimKey = req.get('actiPrimKey', -1)
            postPrimKey = req.get('postPrimKey', -1)
            recvPrimKey = req.get('recvPrimKey', -1)
            content = req.get('content', '')
            try:
                action = NewActionDetail.objects.get(pk=actiPrimKey)
                poster = UserInfo.objects.get(pk=postPrimKey)
                receiver = UserInfo.objects.get(pk=recvPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            NewActionComment.objects.create(action=action, content = content,
                                    poster=poster, receiver=receiver)
                                    
            response['result'] = 0
    except:
        response['result'] = 1
    return HttpResponse(simplejson.dumps(response))

def get_action_brief_list(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug(", post: " + request.raw_post_data)
            userPrimKey = req.get('userPrimKey', -1)
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))

            action_brief_list = []
            actions = user.myActions.all().order_by('-timestamp')
            for action in actions:
                action_brief_list.append(action.getActionBrief())
            response['result'] = 0
    except:
        response['result'] = 1

    paginator = Paginator(action_brief_list, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    response['actionList'] = resp
    json = simplejson.dumps(response)
    return HttpResponse(json)

def get_action_detail(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug(", post: " + request.raw_post_data)
            actionPrimKey = req.get('actionPrimKey', -1)
            try:
                action = NewActionDetail.objects.get(pk=actionPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            actionDetail = action.getActionBrief()
            comments = action.getCommentList() 
            response['result'] = 0
    except:
        response['result'] = 1

    paginator = Paginator(comments, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    actionDetail['comments'] = resp
    response['actionDetail'] = actionDetail
    json = simplejson.dumps(response)
    return HttpResponse(json)
    
def get_status_detail(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug(", post: " + request.raw_post_data)
            statusPrimKey = req.get('statusPrimKey', -1)
            try:
                status = NewUserStatus.objects.get(pk=statusPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            statusDetail = status.getStatusBrief()
            messages = status.getMessageList()
            response['result'] = 0
    except:
        response['result'] = 1

    paginator = Paginator(messages, 15)
    page = request.GET.get('page', 1)
    try:
        resp = paginator.page(page).object_list
    except:
        resp = []
    statusDetail['replies'] = resp
    response['statusDetail'] = statusDetail
    json = simplejson.dumps(response)
    return HttpResponse(json)
    
def get_app_comments(request):
    response = {}
    response['result'] = -1
    #if True:
    try:
        if request.method == 'POST':
            #logger.debug("get app comments, post: " + request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            userPrimKey = req.get('userPrimkey', -1)
            logger.debug("userPrimKey: " + str(userPrimKey))
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))
            exist_app_names = AppInfo.objects.values_list('appname',
                                                            flat=True)
            exist_app_names = set(exist_app_names)
            shared_app_names = user.appinfo_set.values_list('appname',
                                                            flat=True)
            shared_app_names = set(shared_app_names)

            app_name = base64.b64encode(req.get('appName', 'NULL').encode('utf-8'))
            app_name += '\n'
            logger.debug('encoded app name: ' +app_name)
            app_size = long(req.get('appSize', '0'))
            app_icon = req.get('appIcon', 'NULL')

            if app_name not in exist_app_names:
                app_item = AppInfo(appname=app_name,
                                    apk_size=long(app_size),
                                    from_user=True)
                feed = app_name
                md5obj = hashlib.md5(feed.encode('utf-8'))
                fileName = md5obj.hexdigest() + ".png"
                file = open('./media/appIcon/'+fileName, 'wb')
                file.write(base64.b64decode(app_icon))
                file.close()

                app_item.icon_url = fileName
                app_item.save()
                app_item.users.add(user)
            elif app_name not in shared_app_names:
                try:
                    app_item = AppInfo.objects.get(appname=app_name)
                except:
                    return HttpResponse(simplejson.dumps(response))

                app_item.users.add(user)
            else:
                app_item = AppInfo.objects.get(appname=app_name)

            response['result'] = 0
            response['appInfo'] = app_item.getAppInfo()
            response['commentList'] = app_item.getCommentList()
            #response['descript'] = base64.b64decode(app_item.descript)
    except:
        response['result'] = 1
    json = simplejson.dumps(response)
    return HttpResponse(json)
    
def post_new_action(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            userPrimKey = req.get('userPrimkey', -1)
            app_name = base64.b64encode(req.get('appName', 'NULL').encode('utf-8'))
            app_name += '\n'
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
                app = AppInfo.objects.get(appname=app_name)
            except:
                return HttpResponse(simplejson.dumps(response))

            comment = base64.b64encode(req.get('comment', '').encode('utf-8'))
            commentType = req.get('commentType', 0)

            action = NewActionDetail.objects.create(initiator=user, app=app, comment=comment)
            action.save()

            externalInfo = ExternalActionInfo.objects.create(action=action, commentType=commentType)           
            externalInfo.save()
            
        response['result'] = 0
    except:
        response['result'] = 1
    json = simplejson.dumps(response)
    return HttpResponse(json)

def get_user_newsfeed_list(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            req = simplejson.loads(request.raw_post_data)
            #logger.debug(", post: " + request.raw_post_data)
            userPrimKey = req.get('userPrimKey', -1)
            try:
                user = UserInfo.objects.get(pk=userPrimKey)
            except:
                return HttpResponse(simplejson.dumps(response))

            action_brief_list = []
            actions = user.myActions.all().order_by('-timestamp')
            for action in actions:
                action_brief_list.append(action.getActionBrief())
            response['result'] = 0
    except:
        response['result'] = 1

    response['actionList'] = action_brief_list
    json = simplejson.dumps(response)
    return HttpResponse(json)
