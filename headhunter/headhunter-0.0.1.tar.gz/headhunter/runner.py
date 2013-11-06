from pika import BlockingConnection, ConnectionParameters
import types
import marshal

class HunterRunner(object):
  def __init__(self, amqp_server, queue_name):
    self.parameters = ConnectionParameters(amqp_server)
    self.queue_name = queue_name
  
  def process(self, channel, method, properties, body):
    code_object = marshal.loads(body)
    generated_function = types.FunctionType(code_object,
                           globals(), '<network>')
    
    generated_function()
    
    channel.basic_ack(delivery_tag = method.delivery_tag)
  
  def run(self, *argv):
    connection = BlockingConnection(self.parameters)
    channel = connection.channel()
    
    try:
      channel.queue_declare(self.queue_name, durable = True)
      
      channel.basic_consume(self.process, queue = self.queue_name)
      channel.start_consuming()
    finally:
      connection.close()