# MonsterSDK 1.0 by msjavan
# Javan.it@gmail.com

from botocore.config import Config
from pprint import pprint
import requests
import boto3


endpoint1 = "http://127.0.0.1:8081/"
endpoint2 = "http://127.0.0.1:8082/"
endpoint3 = "http://127.0.0.1:8083/"
endpoint4 = "http://127.0.0.1:8084/"
endpoint5 = "http://127.0.0.1:8085/"
endpoint6 = "http://127.0.0.1:8086/"
endpoint7 = "http://127.0.0.1:8087/"
endpoint8 = "http://127.0.0.1:8088/"


class MyMonster:
    token = None
    endpoint = None

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = self.getToken(
            self.endpoint, user="test:tester", password="testing")

    def getToken(self, endpoint, user, password):
        headers = {'X-Storage-User': user, 'X-Storage-Pass': password}
        response = requests.get(endpoint + "auth/v1.0", headers=headers)
        print(response.text)
        print(response.headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            return 0
        else:
            token = response.headers['X-Storage-Token']
            return (token)

    def healthCheck(self):
        response = requests.get(self.endpoint + "healthcheck")
        print(response.status_code)
        print(self.endpoint, response.text)

    def getInfo(self):
        response = requests.get(self.endpoint + "info")
        print(response.status_code)
        pprint(response.text)

    def getObjectInfo(self, container, Object):
        headers = {'X-Auth-Token': self.token}
        response = requests.get(
            self.endpoint + "v1/AUTH_test" + container + Object, headers=headers)
        print(response.status_code)
        return (response.text)

    def getContainerInfo(self, container):
        headers = {'X-Auth-Token': self.token}
        response = requests.get(
            self.endpoint + "v1/AUTH_test" + container, headers=headers)
        print(response.status_code)
        print(response.text)
        print(response.headers)
        return response.text

    def createContainer(self, container):
        headers = {'X-Auth-Token': self.token}

        response = requests.put(
            self.endpoint + "v1/AUTH_test"+container, headers=headers,)
        print(response.status_code)
        print(response.headers)
        print(response.text)

    def createObject(self, container, Object, content):
        headers = {'X-Auth-Token': self.token}

        response = requests.put(self.endpoint + "v1/AUTH_test" +
                                container + Object, headers=headers, data=content)
        print(response.status_code)
        print(response.text)

    def deleteContainer(self, container):
        headers = {'X-Auth-Token': self.token}

        response = requests.delete(
            self.endpoint + "v1/AUTH_test" + container, headers=headers,)
        print(response.status_code)
        print(response.headers)

    def deleteObject(self, container, Object):
        headers = {'X-Auth-Token': self.token}

        response = requests.delete(
            self.endpoint + "v1/AUTH_test" + container + Object, headers=headers,)
        print(response.status_code)
        print(response.text)

    def createObjectMetadata(self, container, Object, key, value):
        headers = {'X-Auth-Token': self.token,
                   'X-Object-Meta-' + key: value, 'charset': 'UtF-8'}

        response = requests.post(
            self.endpoint + "v1/AUTH_test" + container + Object,  headers=headers, )
        print(response.status_code)
        print(response.text)

    def setExpirerAt(self, container, Object, value):
        headers = {'X-Auth-Token': self.token,
                   'X-Delete-At': value, 'charset': 'UtF-8'}

        response = requests.post(
            self.endpoint + "v1/AUTH_test" + container + Object,  headers=headers, )
        print(response.status_code)
        print(response.text)

    def setExpirerAfter(self, container, Object, value):
        headers = {'X-Auth-Token': self.token,
                   'X-Delete-After': value, 'charset': 'UtF-8'}

        response = requests.post(
            self.endpoint + "v1/AUTH_test" + container + Object,  headers=headers, )
        print(response.status_code)
        print(response.text)

    def viewObjectMetadata(self, container, Object):
        headers = {'X-Auth-Token': self.token}

        response = requests.head(
            self.endpoint + "v1/AUTH_test"+container + Object,  headers=headers,)
        #print (response.status_code)
        #print (response.headers)
        return response.headers

    def CopyObject(self, srcContainer, dstContainer, srcObject, destObject):
        headers = {'X-Auth-Token': self.token,
                   'X-Copy-From': srcContainer + srcObject}

        response = requests.put(
            self.endpoint + "v1/AUTH_test" + dstContainer + destObject, headers=headers, )
        print(response.status_code)
        print(response.text)

    def MakePublic(self, container):
        headers = {'X-Auth-Token': self.token,
                   'X-Container-Read': '.r:*,.rlistings'}

        response = requests.post(
            self.endpoint + "v1/AUTH_test" + container,  headers=headers, )
        print("Making public... " + self.endpoint + "v1/AUTH_test" + container)
        print(response.status_code)
        print(response.text)

    def GetPublicURL(self, container, obj):
        self.MakePublic(container)
        print(self.endpoint + "v1/AUTH_test" + container + obj)


class MyMonsterS3:
    s3_config = None
    endpoint = None
    connection = None

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.s3_config = Config(region_name='afranet',
                                signature_version='s3')  # or s3v4
        self.connection = boto3.client('s3',
                                       'afranet',
                                       endpoint_url=endpoint,
                                       aws_access_key_id="test:tester",
                                       aws_secret_access_key="testing", config=self.s3_config)

    def getConnection(self):
        return self.connection
