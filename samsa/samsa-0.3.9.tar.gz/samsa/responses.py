from collections import namedtuple

# From MetadataRequest
MetadataResponse = namedtuple('MetadataResponse',
                              ['brokers', 'topics'])
BrokerMetadata = namedtuple('BrokerMetadata',
                            ['id', 'host', 'port'])
TopicMetadata = namedtuple('TopicMetadata',
                           ['topic', 'partitions', 'error_code'])
PartitionMetadata = namedtuple('PartitionMetadata',
                               ['partition', 'leader', 'replicas',
                                'isr', 'error_code'])
