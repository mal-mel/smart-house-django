from __future__ import absolute_import, unicode_literals
from celery import Celery
import requests
from django.core.mail import send_mail
from django.http import HttpResponse
from coursera_house import settings
from .models import Setting

celery = Celery('tasks', broker='amqp://localhost//')
header = {
        'Authorization': 'Bearer 77ca72a6c84222329dfb17e627212e8accda850dcebd6b484f74db76f1978b15'
    }


@celery.task()
def smart_home_manager():

    try:
        context = \
            requests.get(settings.SMART_HOME_API_URL, headers=header)
        if context.json()['status'] != 'ok':
            return HttpResponse('Some problems w API', status=502)
    except:
        return HttpResponse('Some problems w API', status=502)

    controllers_dict = dict()
    controllers_dict['controllers'] = []
    bedroom_light = None
    curtains = None
    smoke_detector = None
    cold_water = None
    washing_machine = None

    '''controllers_dict['controllers'].append({
        'name': Setting.objects.get(id=1).controller_name,
        'value': Setting.objects.get(id=1).value
    })

    controllers_dict['controllers'].append({
        'name': Setting.objects.get(id=2).controller_name,
        'value': Setting.objects.get(id=2).value
    })'''

    for value in context.json()['data']:
        if value['name'] == 'washing_machine':
            washing_machine = value['value']

        if value['name'] == 'bedroom_light':
            bedroom_light = value['value']

        if value['name'] == 'curtains':
            curtains = value['value']

        if value['name'] == 'smoke_detector':
            smoke_detector = value['value']

        if value['name'] == 'leak_detector':
            leak_detector = value['value']
            if value['value']:
                if {'name': 'cold_water', 'value': False} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'cold_water',
                        'value': False
                    })
                if {'name': 'hot_water', 'value': False} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'hot_water',
                        'value': False
                    })

        if value['name'] == 'cold_water':
            cold_water = value['value']
            if not value['value']:
                if {'name': 'boiler', 'value': False} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'boiler',
                        'value': False
                    })
                if {'name': 'washing_machine', 'value': 'off'} not in controllers_dict['controllers'] \
                        and washing_machine != 'broken':
                    controllers_dict['controllers'].append({
                        'name': 'washing_machine',
                        'value': 'off'
                    })

        if value['name'] == 'boiler_temperature':
            if value['value']:
                if value['value'] < Setting.objects.get(id=2).value * 0.9 and not smoke_detector and cold_water:
                    if {'name': 'boiler', 'value': True} not in controllers_dict['controllers']:
                        controllers_dict['controllers'].append({
                            'name': 'boiler',
                            'value': True
                        })

                elif value['value'] >= Setting.objects.get(id=2).value * 1.1:
                    if {'name': 'boiler', 'value': False} not in controllers_dict['controllers']:
                        controllers_dict['controllers'].append({
                            'name': 'boiler',
                            'value': False
                        })

        if value['name'] == 'outdoor_light':
            if value['value'] < 50 and not bedroom_light and curtains != 'slightly_open':
                if {'name': 'curtains', 'value': 'open'} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'curtains',
                        'value': 'open'
                    })

            elif (value['value'] > 50 or bedroom_light) and curtains != 'slightly_open':
                if {'name': 'curtains', 'value': 'close'} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'curtains',
                        'value': 'close'
                    })

        if smoke_detector:
            if {'name': 'air_conditioner', 'value': False} not in controllers_dict['controllers']:
                controllers_dict['controllers'].append({
                    'name': 'air_conditioner',
                    'value': False
                })
            if {'name': 'bedroom_light', 'value': False} not in controllers_dict['controllers']:
                controllers_dict['controllers'].append({
                    'name': 'bedroom_light',
                    'value': False
                })
            if {'name': 'bathroom_light', 'value': False} not in controllers_dict['controllers']:
                controllers_dict['controllers'].append({
                    'name': 'bathroom_light',
                    'value': False
                })
            if {'name': 'boiler', 'value': False} not in controllers_dict['controllers']:
                controllers_dict['controllers'].append({
                    'name': 'boiler',
                    'value': False
                })
            if {'name': 'washing_machine', 'value': 'off'} not in controllers_dict['controllers'] \
                    and washing_machine != 'broken':
                controllers_dict['controllers'].append({
                    'name': 'washing_machine',
                    'value': 'off'
                })

        if value['name'] == 'bedroom_temperature':
            if value['value'] > Setting.objects.get(id=1).value * 1.1 and not smoke_detector:
                if {'name': 'air_conditioner', 'value': True} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'air_conditioner',
                        'value': True
                    })

            elif value['value'] < Setting.objects.get(id=1).value * 0.9:
                if {'name': 'air_conditioner', 'value': False} not in controllers_dict['controllers']:
                    controllers_dict['controllers'].append({
                        'name': 'air_conditioner',
                        'value': False
                    })

    for d in controllers_dict['controllers']:
        for c in context.json()['data']:
            if d['name'] == c['name'] and d['value'] == c['value']:
                controllers_dict['controllers'].remove(d)

    try:
        if controllers_dict['controllers']:
            r = requests.post(settings.SMART_HOME_API_URL, headers=header,
                              json=controllers_dict)
            if r.json()['status'] != 'ok':
                return HttpResponse('Some problems w API', status=502)
    except:
        return HttpResponse('Some problems w API', status=502)

    return controllers_dict['controllers']
