#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

__author__ = 'Michael Liao'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'SmartHome',
        'password': 'SmartHome',
        'db': 'SmartHomeDb'
    },
    'session': {
        'secret': 'Awesome'
    }
}
