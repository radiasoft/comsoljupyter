#

CSSESSIONID = 'CSSESSIONID'
JSESSIONID = 'JSESSIONID'

def search_in_cookie_jar(jar, name):
    for cookie in jar:
        if cookie.name == name:
            return cookie
