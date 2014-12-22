"""
Class for Handling KeystoneEvents in OpenStack's RabbitMQ/QPID

Uses either pika or proton libraries for handling the AMQP protocol, depending whether the message broker is RabbitMQ or QPID, and then implements 
the necessary callbacks for Keystone events (tenant creation)
"""

#############       NOTICE         ######################
# ProZaC is a fork of ZabbixCeilometer-Proxy (aka ZCP), 
# which is Copyright of OneSource Consultoria Informatica (http://www.onesource.pt). 
# For further information about ZCP, check its github : 
# https://github.com/clmarques/ZabbixCeilometer-Proxy  
##########################################################
### ProZaC added functionalities (in this module) ######## 
#
# - support to logging 
# - support for an AMQP server distinct from nova 
# - support to QPID
### --------------------------- ##########################

__copyright__ = "Istituto Nazionale di Fisica Nucleare (INFN)"
__license__ = "Apache 2"
__contact__ = "emidio.giorgio@ct.infn.it"
__date__ = "15/11/2014"
__version__ = "0.9"


import json
import pika

class ProjectEvents:

    def __init__(self, rpc_type, rpc_host, rpc_user, rpc_pass, zabbix_handler):

        self.rpc_type = rpc_type
        self.rpc_host = rpc_host
        self.rpc_user = rpc_user
        self.rpc_pass = rpc_pass
        self.zabbix_handler = zabbix_handler

        self.logger=zabbix_handler.logger
        self.logger.info('Projects listener started')

    def keystone_listener(self):

        self.logger.info("Contacting keystone rpc on host %s (rpc type %s) " %(self.rpc_host,self.rpc_type))

        if self.rpc_type == 'rabbitmq':
            self.keystone_amq_rabbitmq()
        elif self.rpc_type == 'qpid':
            self.keystone_amq_qpid()

    def keystone_amq_rabbitmq(self):
        """
        Method used to listen to keystone events (with rabbitmq amq)
        """

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rpc_host,
                                                                       credentials=pika.PlainCredentials(
                                                                           username=self.rpc_user,
                                                                           password=self.rpc_pass)))
        channel = connection.channel()
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        # exchange name should be made available as option, maybe advanced
        channel.exchange_declare(exchange='keystone', type='topic')
        channel.queue_bind(exchange='openstack', queue=queue_name, routing_key='notifications.#')
        channel.queue_bind(exchange='keystone', queue=queue_name, routing_key='keystone.#')
        channel.basic_consume(self.keystone_callback_rabbitmq, queue=queue_name, no_ack=True)
        channel.start_consuming()

    def keystone_callback_rabbitmq(self, ch, method, properties, body):
        """
        Method used by method keystone_amq() to filter messages by type of message.

        :param ch: refers to the head of the protocol
        :param method: refers to the method used in callback
        :param properties: refers to the proprieties of the message
        :param body: refers to the message transmitted
        """
        payload = json.loads(body)

        if payload['event_type'] == 'identity.project.created':
            
            tenant_id = payload['payload']['resource_info']
            tenants = self.zabbix_handler.get_tenants()
            tenant_name = self.zabbix_handler.get_tenant_name(tenants, tenant_id)
	    self.logger.info("New project (%s) created -> corresponding host group created on zabbix" %(tenant_name))
            self.zabbix_handler.group_list.append([tenant_name, tenant_id])
            self.zabbix_handler.create_host_group(tenant_name)

        elif payload['event_type'] == 'identity.project.deleted':
            
            tenant_id = payload['payload']['resource_info']
            tenants = self.zabbix_handler.get_tenants()
            tenant_name = self.zabbix_handler.get_tenant_name(tenants, tenant_id)
            self.logger.info("Project %s deleted -> Corresponding host group deleted from zabbix" %(tenant_name))
            self.zabbix_handler.project_delete(tenant_id)


    ##  QPID  
    def keystone_amq_qpid(self):

        from qpid.messaging.endpoints import Connection

        connection = Connection(self.rpc_host,username="guest",password="guest")
        connection.open()
        session = connection.session()
        receiver = session.receiver('openstack/notifications.#')
        self.logger.debug ("Starting keystone loop")
        self.keystone_qpid_loop (receiver)

    def keystone_qpid_loop(self,recv):
        
        while True:
            message = recv.fetch()
            event_type=message.content['event_type'] 
            self.logger.debug("Caught event %s" %(event_type))

            if event_type == "identity.project.created":
                payload=message.content['payload']
                tenant_id=payload['resource_info']
                tenants = self.zabbix_handler.get_tenants()
                tenant_name = self.zabbix_handler.get_tenant_name(tenants, tenant_id)
                self.logger.info("New project (%s) created -> corresponding host group created on zabbix" %(tenant_name))
                self.zabbix_handler.group_list.append([tenant_name, tenant_id])
                self.zabbix_handler.create_host_group(tenant_name)

            elif event_type == "identity.project.deleted":
                payload=message.content['payload']
                tenant_id=payload['resource_info']
                tenant_name = self.zabbix_handler.get_tenant_name(tenants, tenant_id)
                self.logger.info("Project %s deleted -> Corresponding host group deleted from zabbix" %(tenant_name))
                self.zabbix_handler.project_delete(tenant_id)
                 

            else: pass 
