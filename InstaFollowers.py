#!/usr/bin/env python2.7

"""Discover who unfollowed you on Instagram."""

import json, webbrowser
from urllib2 import urlopen, URLError
from urlparse import urlparse
from time import time
from os import rename, remove

__author__ = "Palmer Paul"
__version__ = "1.0.2"
__email__ = "pzpaul2002@yahoo.com"

class Application(object):
    def __init__(self):
        self.followers = []
        self.data = self.load_data()
        
    def load_data(self):
        try:
            fp_read = open("instafollowersData.txt", "r")
            try:
                data = json.load(fp_read)
                fp_read.close()
            except ValueError:
                fp_read.close()
                data = self.load_error()
        except IOError:
            data = self.load_error()
        return data

    def load_error(self):
        token = self.authenticate()
        user_id = self.get_userid(token)
        data = (token, user_id, {time(): self.update(token, user_id)})
        write = open("temp.txt", "w")
        json.dump(data, write)
        write.close()
        try:
            rename("temp.txt", "instafollowersData.txt")
        except OSError:
            remove("instafollowersData.txt")
            rename("temp.txt", "instafollowersData.txt")
        return data
        
    def authenticate(self):
        webbrowser.open("http://bit.ly/1pbkymQ")
        url = raw_input("After authorizing this app, copy the entire URL from the address bar and paste it here (it doesn't matter if the page cannot be found): ")
        while not url.startswith("http://localhost:8515/#"):
            url = raw_input("Please copy and paste the ENTIRE URL: ")
        url = urlparse(url)[5]
        token = url[url.find("access_token=")+13:]
        return token

    def get_userid(self, token):
        return token[:token.find(".")]

    def update(self, token, user_id):
        self.followers = []
        next_url = "https://api.instagram.com/v1/users/" + user_id + "/followed-by?access_token=" + token
        while True:
            err_cnt = 0
            while True:
                try:
                    request = json.loads(urlopen(next_url).read())
                    break
                except URLError:
                    print "Error: Could not access the Instagram API"
                    err_cnt += 1
                    if err_cnt == 5:
                        print "The Instagram API is unreachable at the moment. Please make sure that you are connected to the internet and try again."
                        raise SystemExit
                    else:
                        print "Retrying..."

            for user in request["data"]:
                self.followers.append(user["username"])

            try:
                next_url = request["pagination"]["next_url"]
            except KeyError:
                break
        return self.followers
        
    def save(self):
        self.data[2][time()] = self.followers
        write = open("temp.txt", "w")
        json.dump(self.data, write)
        write.close()
        try:
            rename("temp.txt", "instafollowersData.txt")
        except OSError:
            remove("instafollowersData.txt")
            rename("temp.txt", "instafollowersData.txt")
            
    def compare(self):        
        follow_hist = self.data[2]
        last = follow_hist[max(follow_hist.keys())]
        current = self.update(self.data[0], self.data[1])
        self.save()

        gained = []
        for follower in range(len(current)):
            if not current[follower] in last:
                gained.append(current[follower])

        lost = []
        for follower in range(len(last)):
            if not last[follower] in current:
                lost.append(last[follower])

        return (gained, lost)

    def main(self):
        analysis = self.compare()
        print "Total followers: " + str(len(self.followers))
        print "Gained: " + str(len(analysis[0]))
        for user in range(len(analysis[0])):
            print str(user+1) + ": " + analysis[0][user]
        print "Lost: " + str(len(analysis[1]))
        for user in range(len(analysis[1])):
            print str(user+1) + ": " + analysis[1][user]
        print

myApp = Application()
myApp.main()
