import struct

from samsa.responses import (
    MetadataResponse, BrokerMetadata, TopicMetadata, PartitionMetadata
)

# N.B.: This file is written with an eye to minimizing string copies. When
#       adding new API calls, please keep that in mind.

# TODO: Figure out how to do this entirely copy-free (but configurable)

## API KEYS

## ProduceRequest       0
## FetchRequest         1
## OffsetRequest        2
## MetadataRequest      3
## LeaderAndIsrRequest  4
## StopReplicaRequest   5
## OffsetCommitRequest  6
## OffsetFetchRequest   7


## All version numbers are currently 0

CORRELATION_ID = 42 # we don't need this
CLIENT_ID = 'samsa'
HEADER_LEN= 19

def _write_header(api_key, msg_bytes, api_version=0):
    struct.pack_into(
        '>ihhih5s',
        msg_bytes, 0,
        len(msg_bytes) - 4, api_key, api_version,
        CORRELATION_ID, 5, CLIENT_ID
    )


def _unpack(fmt, buff, offset):
    """Decode a format string and return new offset. Use '!s' for a string"""
    if fmt == '!s':
        fmt = '!%ds' % struct.unpack_from('!h', buff, offset)
        offset += 2

    output = struct.unpack_from(fmt, buff, offset)
    offset += struct.calcsize(fmt)
    return output, offset


def encode_metadata_request(topics=None):
    topics = [] if topics is None else topics
    topics_len = [len(t) for t in topics] # we use this a couple times
    msg_len = 4 + sum(topics_len)
    output = bytearray(HEADER_LEN + msg_len)

    # Write the header
    _write_header(3, output)

    # Write the message data
    struct.pack_into(
        '>i' + ''.join('%ds' % lt for lt in topics_len),
        output, HEADER_LEN,
        len(topics), *topics
    )
    return output

def decode_metadata_request(buff):
    """Decode a metadata request response"""
    pos = 0

    # Unpack brokers
    brokers = {}
    (_,num_brokers),pos = _unpack('>ii', buff, pos) # skipping correlation_id

    for i in xrange(num_brokers):
        (b_id,),pos = _unpack('!i', buff, pos)
        (host,),pos = _unpack('!s', buff, pos)
        (port,),pos = _unpack('!i', buff, pos)
        brokers[b_id] = BrokerMetadata(b_id, host, port)

    topics = {}
    (num_topics,),pos = _unpack('>i', buff, pos)
    for i in xrange(num_topics):
        (t_err,),pos = _unpack('!h', buff, pos)
        (t_nam,),pos = _unpack('!s', buff, pos)
        (num_part,),pos = _unpack('!i', buff, pos)
        topics[t_nam] = TopicMetadata(t_nam, {}, t_err)
        for j in xrange(num_part):
            (p_err,p_id,p_ldr,num_rep),pos = _unpack('!hiii', buff, pos)
            p_reps,pos = _unpack('!' + 'i'*num_rep, buff, pos)
            (num_isr,),pos = _unpack('!i', buff, pos)
            p_isr,pos = _unpack('!' + 'i'*num_isr, buff, pos)
            topics[t_nam].partitions[p_id] = PartitionMetadata(
                p_id, p_ldr, p_reps, p_isr, p_err
            )
    return MetadataResponse(brokers, topics)
