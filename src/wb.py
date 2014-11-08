#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lane's Weibo Client Application Beta, Nothing Reserved
"""

from http_helper import *
from sdk import Client
import sys, os
import pickle
import getpass
import argparse
import urllib, urllib2
import configparser

version = sys.version[0]
input = raw_input if version == '2' else input
reload(sys)
sys.setdefaultencoding('utf8')

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY      = config['Weibo']['API_KEY']
API_SECRET   = config['Weibo']['API_SECRET']
REDIRECT_URI = config['Weibo']['REDIRECT_URI']

##########################################################################
# Functions are defined below
##########################################################################
def log_in_to_weibo():
    """
    Log in to weibo and get the ACCESS_TOKEN.
    If success, store it to 'token' file,
    if not, do nothing.
    """

    print "please enter your username and password below\n"

    client = Client(API_KEY, API_SECRET, REDIRECT_URI)

    USERID = input("username: ")
    USERPASSWD = getpass.getpass("password: ") # getpass() makes password invisible

    print('')
    print('logging...')
    code = make_access_token(client, USERID, USERPASSWD)
    if not code: # while log in failed
        print "" # a blank line to make better look
        print "bad username or password, please try again!\n"

    # after got code, store it
    else:
        client.set_code(code)
        fw = open('token', 'wb')
        pickle.dump(client.token, fw)
        fw.close()
        print "log in to weibo.com successfully"

def log_out_from_weibo():
    """delete login informations"""

    os.remove('token')

def make_access_token(client, USERID, USERPASSWD):
    """
    Refer to: http://www.cnblogs.com/wly923/archive/2013/04/28/3048700.html
    This function can automatically get 'code' from redirected URL and return it.
    """

    params = urllib.urlencode({
        'action':'submit',
        'withOfficalFlag':'0',
        'ticket':'',
        'isLoginSina':'',
        'response_type':'code',
        'regCallback':'',
        'redirect_uri':REDIRECT_URI,
        'client_id':API_KEY,
        'state':'',
        'from':'',
        'userId':USERID,
        'passwd':USERPASSWD,
        })

    login_url = 'https://api.weibo.com/oauth2/authorize'

    url = client.authorize_url
    content = urllib2.urlopen(url)

    if content:
        headers = { 'Referer' : url }
        request = urllib2.Request(login_url, params, headers)
        opener = get_opener(False)
        urllib2.install_opener(opener)

        try:
            f = opener.open(request)
            return_redirect_uri = f.url
        except urllib2.HTTPError, e:
            return_redirect_uri = e.geturl()

        if return_redirect_uri == login_url:
            code = False
        else:
            code = return_redirect_uri.split('=')[1]

    else:
        code = False

    return code

def update_access_token():
    """Try to load ACCESS_TOKEN from 'token' file"""

    try:
        fr = open('token', 'rb')
        ACCESS_TOKEN = pickle.load(fr)
        fr.close()

    except IOError:
        ACCESS_TOKEN = None

    return ACCESS_TOKEN

def get_comments_to_me(client, start_page, end_page):
    """Download comments from 'start_page' to 'end_page'"""

    my_page = start_page

    fw = open('comments.txt', 'wb')

    while my_page <= end_page:
        try:
            print('Page {} is downloading'.format(my_page))
            received = client.get('comments/to_me', count = 20, uid = 1804547715, page = my_page)

        except:
            print('Page {} is downloading has failed'.format(my_page))
            continue

        fw.write('\n\nPage {}:\n'.format(my_page).encode('utf8'))
        for item in received.comments:
            to_be_written = '{0}: {1} by {2}\n'.format(item.created_at, item.text, item.user.name)
            fw.write(to_be_written.encode('utf8'))

        fw.flush()
        my_page += 1

    fw.close()
    print('All the comments have been downloaded')


def get_friends_timeline(client, count):
    """Show friends_timeline in the screen"""

    print('') # a blank line makes better look
    print("getting latest %s friend's weibo...\n") % count

    received = client.get('statuses/friends_timeline', count = count)

    index = int(count) # used in No.{index} below
    for item in received.statuses[::-1]: # from old to new
        retweet = item.get('retweeted_status') # if this is retweet or not

        # print normal content first
        print\
            ('No.{}:\n{} by @{}:\n{}'.format
                (
                    str(index),
                    item.created_at[:16],
                    item.user.name,
                    item.text,
                ).encode('utf8')
            )

        # if this is not retweet, just print a blank line
        if not retweet:
            print('')

        # if this is retweet, print the retweeted content
        else:
            print('-----------------')
            print\
            ('{} by @{}:\n{}'.format
                (
                    item.retweeted_status.created_at[:16],
                    item.retweeted_status.user.name,
                    item.retweeted_status.text,
                ).encode('utf8')
            )
            print('-----------------\n')

        index -= 1

def post_statuses_update(client, text):
    """Update a new weibo(text only) to Sina"""

    print('')
    print('sending...\n')

    try:
        client.post('statuses/update', status = text)
        print('-----------------')
        print(text)
        print('-----------------')
        print('has been successfully posted!\n')

    except RuntimeError as e:
        print("sorry, send failed because: {}\n".format(str(e)))

def post_statuses_upload(client, text, picture):
    """Upload a new weibo(with picture) to Sina"""

    # bug !!! 2014.11.8 zhanglin
    # bug description:
    # can't open 'picture'
    # for example:
    # f = open('/Dropbox/APP/FarBox/zhanglintc.farbox.com/_image/bird.jpg', 'rb') is OK
    # but
    # f = open(picture, 'rb') is NOT ok
    # even though picture == '/Dropbox/APP/FarBox/zhanglintc.farbox.com/_image/bird.jpg' is True
    # don't know why

    print('')
    print('sending...\n')

    try:
        f = open(picture, 'rb')
        client.post('statuses/upload', status = text, pic = f)
        f.close()

        print('-----------------')
        print(text)
        print('-----------------')
        print('has been successfully posted!\n')

    except (RuntimeError, IOError) as e:
        print("sorry, send failed because: {}\n".format(str(e)))

def creat_parser():
    parser = argparse.ArgumentParser(
        prog = "wb",
        # usage = 'wb -option [option1, option2...]',
        description = "wb -- A command-line tool for Weibo",
        epilog = 'This code is out sourced on Github,\
                    please visit https://github.com/zhanglintc/wb\
                    for further infomations',
        prefix_chars = '-/',
        fromfile_prefix_chars = '@',
        argument_default = argparse.SUPPRESS,
        )

    parser.add_argument('-authorize', metavar = '-a', nargs = '?', const = 'True', help = "sign in to 'weibo.com'")
    parser.add_argument('-delete', metavar = '-d', nargs = '?', const = 'True', help = "delete your token infomation") 
    parser.add_argument('-get', metavar = '-g', nargs = '?', const = 5, help = "get latest N friend's timeline")
    parser.add_argument('-image', metavar = '-i', nargs = 2, help = "post a new weibo with image")
    parser.add_argument('-post', metavar = '-p', nargs = 1, help = "post a new weibo")
    parser.add_argument('-tweet', metavar = '-t', nargs = 1, help = "post a new weibo(alias of -p)")

    return parser

##########################################################################
##########################################################################

if __name__ == "__main__":
    ACCESS_TOKEN = update_access_token()
    client = Client(API_KEY, API_SECRET, REDIRECT_URI, ACCESS_TOKEN)

    parser = creat_parser()
    parameters = vars(parser.parse_args())
    # print parameters

    if not parameters:
        print ''
        print '- Note: type "wb -h/--help" to see usages.\n'

    elif parameters.get('authorize'):
        log_in_to_weibo()

    elif parameters.get('delete'):
        log_out_from_weibo()

    elif parameters.get('get'):
        get_friends_timeline(client, parameters['get'])

    elif parameters.get('image'):
        post_statuses_upload(client, parameters['image'][0], parameters['image'][1])

    elif parameters.get('post'):
        post_statuses_update(client, parameters['post'][0])

    elif parameters.get('tweet'):
        post_statuses_update(client, parameters['tweet'][0])

    else:
        pass





