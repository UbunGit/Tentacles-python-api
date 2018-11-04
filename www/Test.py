import unittest
import requests
import re, time, json, logging, hashlib, base64, asyncio

class MyTestCase(unittest.TestCase):

    def test_deleteuser(self):
        print("删除用户 测试")
        url='http://192.168.1.27:9000/api/user/delete'
        data={
            "phone":"13923497592"
        }
        r = requests.post(url,data)
        print(r.status_code)
        print(r.headers['content-type'])
        print(r.encoding)
        print(r.json())
        self.assertEqual(r.status_code, 200)

    def test_register(self):
        '''phone,  passwd, recommendCode=None, permissions=0'''
        print("用户注册 测试")
        sha1_passwd = ':000000'
        url = 'http://192.168.1.27:9000/api/register'
        data={
            "phone":"13923497592",
            "passwd":hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
        }

        r = requests.post(url,data)

        print(r.status_code)
        print(r.headers['content-type'])
        print(r.encoding)
        print(r.json())
        self.assertEqual(r.status_code, 200)

    def test_updateuser(self):
        '''phone=None, userName=None, passwd=None, headImage=None'''
        print("用户更新会员信息 测试")
        url = 'http://192.168.1.27:9000/api/user/update'
        data={
            "userName":"love"
        }

        r = requests.post(url,data)

        print(r.status_code)
        print(r.headers['content-type'])
        print(r.encoding)
        print(r.json())
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        '''phone, passwd,verCode=None'''
        print("用户登录 测试")
        url = 'http://192.168.1.27:9000/api/users/login'
        data={
            "phone":"13923497592",
            "passwd":hashlib.sha1(":000000".encode('utf-8')).hexdigest(),
        }

        r = requests.post(url,data)

        print(r.status_code)
        print(r.headers['content-type'])
        print(r.encoding)
        print(r.json())
        self.assertEqual(r.status_code, 200)



if __name__ == '__main__':

    print("")



