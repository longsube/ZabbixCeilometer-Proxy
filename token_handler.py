#!/usr/bin/python
"""
Class for requesting authentication tokens to Keystone

This class provides means to requests for authentication tokens to be used with OpenStack's Ceilometer, Nova and RabbitMQ
"""
#############       NOTICE         ######################
# ProZaC is a fork of ZabbixCeilometer-Proxy (aka ZCP), 
# which is Copyright of OneSource Consultoria Informatica (http://www.onesource.pt). 
# For further information about ZCP, check its github : 
# https://github.com/clmarques/ZabbixCeilometer-Proxy  
##########################################################
### ProZaC added functionalities (in this module) ######## 
#
# - support of token renewal : proxy restart is no longer needed each hour
# - support to logging
# 
### --------------------------- ##########################

__copyright__ = "Istituto Nazionale di Fisica Nucleare (INFN)"
__license__ = "Apache 2"
__contact__ = "emidio.giorgio@ct.infn.it"
__date__ = "15/11/2014"
__version__ = "0.9"

import urllib2
import json
import time
import logging

class Auth:
    def __init__(self, auth_host, public_port, admin_tenant, admin_user, admin_password):

        self.auth_host = auth_host
        self.public_port = public_port
        self.admin_tenant = admin_tenant
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.logger=logging.getLogger('ZCP')
        self.logger.info("Keystone handler initialized")

    def getToken(self):
        """
        Requests and returns an authentication token to be used with OpenStack's Ceilometer, Nova and RabbitMQ
        :return: The Keystone token assigned to these credentials
        """
        auth_request = urllib2.Request("http://"+self.auth_host+":"+self.public_port+"/v2.0/tokens")
        auth_request.add_header('Content-Type', 'application/json;charset=utf8')
        auth_request.add_header('Accept', 'application/json')
        auth_data = {"auth": {"tenantName": self.admin_tenant,
                              "passwordCredentials": {"username": self.admin_user, "password": self.admin_password}}}
        auth_request.add_data(json.dumps(auth_data))
        auth_response = urllib2.urlopen(auth_request)
        response_data = json.loads(auth_response.read())
        token = response_data['access']['token']['id']
        
        return token

    def getTokenV2(self):
        """
        Requests and returns an authentication token to be used with OpenStack's Ceilometer, Nova and RabbitMQ
        :return: a tuple with 
         - the Keystone token assigned to these credentials a
         - the expiration time (to avoid API REST calls at each Ceilometer or Project thread iteration)
        """
        auth_request = urllib2.Request("http://"+self.auth_host+":"+self.public_port+"/v2.0/tokens")
        auth_request.add_header('Content-Type', 'application/json;charset=utf8')
        auth_request.add_header('Accept', 'application/json')
        auth_data = {"auth": {"tenantName": self.admin_tenant,
                              "passwordCredentials": {"username": self.admin_user, "password": self.admin_password}}}
        auth_request.add_data(json.dumps(auth_data))
        auth_response = urllib2.urlopen(auth_request)
        response_data = json.loads(auth_response.read())

        token_id = response_data['access']['token']['id']
        expiration_time=response_data['access']['token']['expires']
        expiration_timestamp=time.mktime(time.strptime(expiration_time,"%Y-%m-%dT%H:%M:%SZ"))
        
        token={'id':token_id,'expires':expiration_timestamp}

        return token

    
            
