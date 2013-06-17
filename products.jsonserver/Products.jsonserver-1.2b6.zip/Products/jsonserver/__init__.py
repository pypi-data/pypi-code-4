'''\
jsonserver product

patches the zpublisher to provide json-rpc
'''

def initialize(context):
    import jsonrpc

    # do the patching
    jsonrpc.patch_HTTPRequest()
