# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
CSSESSIONID = 'CSSESSIONID'
JSESSIONID = 'JSESSIONID'
RSESSIONID = 'RSESSIONID'

def search_in_cookie_jar(jar, name):
    for cookie in jar:
        if cookie.name == name:
            return cookie
