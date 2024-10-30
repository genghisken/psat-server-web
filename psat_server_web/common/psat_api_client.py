""" Pan-STARRS API

This class enables programmatic access to the Pan-STARRS and ATLAS databases

Args:
    token (string): The Calls are throttled by the Pan-STARRS server, by use of an 
    'authorization token', as described in the api documentation above. 
    There is a free token listed there, but it is throttled at 10 calls per hour. 
    Once a user has an account at the Pan-STARRS webserver, they can get their own token
    allowing 100 calls per hour, or request to be a power user, with infinite usage.

    cache (string): Results can be cached on a local filesystem, by providing 
    the name of a writable directory. If the same calls are made repeatedly, 
    this will be much more efficient.
"""
import os, sys
import requests
import json
import hashlib

class PSATAPIError(Exception):
    def __init__(self, message):
        self.message = message

class psat_client():
    def __init__(self, token, cache=None, endpoint=None, timeout=60.0):
        self.headers = { 'Authorization': 'Token %s' % token }
        self.endpoint = endpoint
        self.timeout = timeout
        self.cache = cache
        if cache and not os.path.isdir(cache):
            message = 'Cache directory "%s" does not exist' % cache
            raise PSATAPIError(message)

    def fetch_from_server(self, method, input):
        url = '%s/%s/' % (self.endpoint, method)
        try:
            r = requests.post(url, data=input, headers=self.headers, timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            raise PSATAPIError('Request timed out')

        if r.status_code == 200:
            try:
                result = r.json()
            except:
                result = {'error': 'Cannot parse Json %s' % r.text}
        elif r.status_code == 400:
            message = 'Bad Request:' + r.text
            raise PSATAPIError(message)
        elif r.status_code == 401:
            message = 'Unauthorized'
            raise PSATAPIError(message)
        elif r.status_code == 429:
            message = 'Request limit exceeded. Either wait an hour, or see API documentation to increase your limits.'
            raise PSATAPIError(message)
        elif r.status_code == 500:
            message = 'Internal Server Error' + r.text
            raise PSATAPIError(message)
        else:
            message = 'HTTP return code %d for\n' % r.status_code
            message += url
            raise PSATAPIError(message)
        return result

    def hash_it(self, input):
        s = json.dumps(input)
        h = hashlib.md5(s.encode())
        return h.hexdigest()

    def fetch(self, method, input):
        if self.cache:
            cached_file = '%s/%s.json' % (self.cache, self.hash_it(method +'/'+ str(input)))
            try:
                result_txt = open(cached_file).read()
                result = json.loads(result_txt)
                return result
            except:
                pass

        result = self.fetch_from_server(method, input)

        if 'error' in result:
            return result

        if self.cache:
            f = open(cached_file, 'w')
            result_txt = json.dumps(result, indent=2)
            f.write(result_txt)
            f.close()

        return result

    def cone(self, ra, dec, radius=5, requestType='all'):
        """ Run a cone search on the Pan-STARRS or ATLAS database.
        Args:
            ra (float): Right Ascension in decimal degrees
            dec (float): Declination in decimal degrees
            radius (float): cone radius in arcseconds (default is 5)
            requestType: Can be 'all' to return all objects in the cone
                Can be 'nearest', only the nearest object within the cone
                Can be 'count', the number of objects within the cone

        Returns a dictionary with:
            objectId: The ID of the nearest object
            separation: the separation in arcseconds
        """
        input = {'ra':ra, 'dec':dec, 'radius':radius, 'requestType':requestType}
        result = self.fetch('cone', input)
        return result

