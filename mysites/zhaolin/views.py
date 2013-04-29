import logging
logger = logging.getLogger('zhaolin_debug')

import base64, hashlib

from zhaolin.models import AppInfo, UserInfo, Collect
from zhaolin import position

from django.http import HttpResponse
from django.utils import simplejson
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

'''
response['result'] = :
-1 user error, need re-login
0  current operation failure, no relation with user
1  successfull
'''

def debug_info(request):
    if request.method == 'POST':
        logger.debug('data posted: %s', request.raw_post_data)
        return HttpResponse(str(len(request.raw_post_data)))
    return HttpResponse(request.method)

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
                collect = Collect.objects.create(userInfo = user)

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
            response['result'] = 0
    except:
        response['result'] = 1

    json = simplejson.dumps(response)
    return HttpResponse(json)

def update_location(request):
    response = {}
    response['result'] = -1
    try:
        if request.method == 'POST':
            logger.debug('update location, posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            renrenId = req.get('renrenId')
            try:
                user = UserInfo.objects.get(renrenId = renrenId)
            except:
                json = simplejson.dumps(response)
                return HttpResponse(json)

            location = req.get('location', '0,0').split(',')

            latitude = float(location[0])
            longitude = float(location[1])
            
            user.latitude = latitude
            user.longitude = longitude
            user.save()
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
            #logger.debug('data posted: %s', request.raw_post_data)
            req = simplejson.loads(request.raw_post_data)
            renrenId = req.get('renrenId')
            try:
                user = UserInfo.objects.get(renrenId = renrenId)
            except:
                return HttpResponse(simplejson.dumps(response))

            appList = req.get('appList', None)

            exist_app_names = AppInfo.objects.values_list('appname',
                                                            flat=True)
            exist_app_names = dict.fromkeys(exist_app_names, True)
            shared_app_names = user.appinfo_set.values_list('appname',
                                                            flat=True)
            shared_app_names = dict.fromkeys(shared_app_names, True)

            for item in appList:
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
            renrenId = req.get('renrenId', '0')
            appName = req.get('appName', '0')
            bCollect = request.GET('bCollect', True)

            try:
                user = UserInfo.objects.get(renrenId = renrenId)
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
            #logger.debug('raw: '+ request.raw_post_data)
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
                    user_info = {}
                    user_info['renrenId'] = friend.renrenId
                    user_info['userName'] = friend.username
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

            nearby_users = []
            tmp_user = UserInfo.objects.get(renrenId = '261843626')
            nearby_users.append(tmp_user)

            for user in nearby_users:
                distance = position.get_distance(longitude, latitude,
                                        user.longitude, user.latitude)
                logger.debug(str(longitude)+' ' + str(user.longitude)+ ' '+ str(latitude) + ' ' + str(user.latitude))
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
                    user_info = {}
                    user_info['renrenId'] = user.renrenId
                    user_info['userName'] = user.username
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
    logger.debug('response to get nearby: ' + json)
    return HttpResponse(json)
