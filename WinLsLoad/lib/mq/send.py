#!/usr/bin/env python
import pika
import logging

logger = logging.getLogger(__name__)

def send(hostname, exchange_name, routing_key_name, msg):
    logger.info("exchange:%s,routing_key:%s,msg:%s", exchange_name, routing_key_name, msg)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        channel.basic_publish(exchange=exchange_name, routing_key=routing_key_name, body=msg)
        connection.close()
        return True
    except Exception, e:
        logger.info(e)
        return False


