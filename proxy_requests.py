#! /usr/bin/python3
import requests
import re
import json
from requests.auth import HTTPBasicAuth


class ProxyRequests:
    def __init__(self, url, country):
        self.sockets = []
        self.url = url
        self.country = country
        if self.country  == "Any" :
            self.country = None
        self.proxy = ""
        self.request = ""
        self.headers = {}
        self.file_dict = {}
        if country != "":
            self.__acquire_sockets()
        self.status_code = ""
        self.proxy_used = ""

    # get a list of sockets from sslproxies.org
    def __acquire_sockets(self):
        r = requests.get("https://www.sslproxies.org/")
        if self.country is not None:
            matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td><td>"+self.country+"</td>", r.text)
            if len(matches) < 1:
                matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td>", r.text)
        else :
            matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td>", r.text)
        revised_list = [m1.replace("<td>", "") for m1 in matches]
        for socket_str in revised_list:
            if self.country is not None:
                self.sockets.append(socket_str[:-5].replace("</td>", ":").replace(":"+self.country, ""))
            else:
                self.sockets.append(socket_str[:-5].replace("</td>", ":"))

    # recursively try proxy sockets until successful GET
    def get(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.get(self.url, timeout=3.0, proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.get()
        else:
            try:
                request = requests.get(self.url, timeout=3.0)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
            except:
                print('working...')
                self.get()

    # recursively try proxy sockets until successful GET with headers
    def get_with_headers(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.get(self.url, timeout=3.0,headers=self.headers, proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.get_with_headers()
        else:
            try:
                request = requests.get(self.url, timeout=3.0,headers=self.headers)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
            except:
                print('working...')
                self.get_with_headers()

    # recursively try proxy sockets until successful POST
    def post(self, data):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url, json=data, timeout=3.0, proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post(data)
        else :
            try:
                request = requests.post(self.url, json=data, timeout=3.0)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
            except:
                print('working...')
                self.post(data)

    # recursively try proxy sockets until successful POST with headers
    def post_with_headers(self, data):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url,
                                        json=data,
                                        timeout=3.0,
                                        headers=self.headers,
                                        proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post_with_headers(data)
        else :
            try:
                request = requests.post(self.url,
                                        json=data,
                                        timeout=3.0,
                                        headers=self.headers)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
            except:
                print('working...')
                self.post_with_headers(data)

    # recursively try proxy sockets until successful POST with file
    def post_file(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url,
                                        files=self.file_dict,
                                        timeout=3.0,
                                        proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post_file()
        else :
            try:
                request = requests.post(self.url,
                                        files=self.file_dict,
                                        timeout=3.0)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
            except:
                print('working...')
                self.post_file()

    # not intended for string or html... a string may work but should be for a json dict response
    def to_json(self):
        try:
            json_resp = json.dumps(json.JSONDecoder().decode(self.request))
        except:
            return json.dumps({'error': 'No JSON Object could be decoded'})
        return json_resp

    def get_headers(self):
        return self.headers

    def set_headers(self, outgoing_headers):
        self.headers = outgoing_headers

    def set_file(self, outgoing_file):
        self.file_dict = outgoing_file

    def get_status_code(self):
        return self.status_code

    def get_proxy_used(self):
        return str(self.proxy_used)

    def __str__(self):
        return str(self.request)


class ProxyRequestsBasicAuth(ProxyRequests):
    def __init__(self, url, username, password, country):
        super().__init__(url,country)
        self.username = username
        self.password = password

    # recursively try proxy sockets until successful GET (overrided method)
    def get(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.get(self.url,
                                       auth=(self.username, self.password),
                                       timeout=3.0,
                                       proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.get()
    # recursively try proxy sockets until successful GET with Headers (overrided method)
    def get_with_headers(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.get(self.url,
                                       auth=(self.username, self.password),
                                       timeout=3.0,
                                       headers=self.headers,
                                       proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.get_with_headers()
    # recursively try proxy sockets until successful POST (overrided method)
    def post(self, data):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url,
                                        json=data,
                                        auth=(self.username, self.password),
                                        timeout=3.0,
                                        proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post(data)

    # recursively try proxy sockets until successful POST with headers (overrided method)
    def post_with_headers(self, data):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url,
                                        json=data,
                                        auth=(self.username, self.password),
                                        timeout=3.0,
                                        headers=self.headers,
                                        proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post_with_headers(data)

    # recursively try proxy sockets until successful POST with file
    def post_file(self):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(0)
            proxies = {"http": "http://" + current_socket, "https": "https://" + current_socket}
            try:
                request = requests.post(self.url,
                                        files=self.file_dict,
                                        auth=(self.username, self.password),
                                        timeout=3.0,
                                        proxies=proxies)
                self.request = request.text
                self.headers = request.headers
                self.status_code = request.status_code
                self.proxy_used = current_socket
            except:
                print('working...')
                self.post_file()

    def __str__(self):
        return str(self.request)


if __name__ == "__main__":
    # example post with headers
    r = ProxyRequests("https://postman-echo.com/post","")
    r.set_headers({"name": "rootVIII", "secret_message": "7Yufs9KIfj33d"})
    r.post_with_headers({"key1": "value1", "key2": "value2"})
    print(r)
    print(r.get_headers())
    print(r.get_status_code())
    # print(r.to_json())
    print(r.get_proxy_used())
