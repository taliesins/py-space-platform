'''
Created on 23-Jun-2014

@author: rjoyce
'''

import os
import yaml

class Service(object):
    """Encapsulates a Space Service"""

    def __init__(self, rest_end_point, name, meta_object):
        self._rest_end_point = rest_end_point
        self._name = name
        self._meta_object = MetaService(name)
        self._collections = {}
        self._methods = {}

    def get_meta_resource(self, resource_type):
        return self._meta_object.get_meta_resource(resource_type)

    def __getattr__(self, attr):
        if attr in self._collections:
            return self._collections[attr]
        if attr in self._methods:
            return self._methods[attr]

        collection = self._meta_object.create_collection(self, attr)
        if collection is not None :
            self._collections[attr] = collection
            return collection
        method = self._meta_object.create_method(self, attr)
        if method is not None:
            self._methods[attr] = method
            return method
        else:
            raise AttributeError

class MetaService(object):

    def __init__(self, name):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        with open(dir_path + '/' + name + '.yml') as f:
            y = yaml.load(f)
            self._meta_collections = y['collections']
            self._meta_methods = y['methods']
            self._meta_resources = y['resources']

    def create_collection(self, service, name):
        if name in self._meta_collections:
            from jnpr.space.platform.core import collection
            return collection.Collection(service, name, self._meta_collections[name])

    def create_method(self, service, name):
        pass

    def get_meta_resource(self, name):
        return self._meta_resources[name]