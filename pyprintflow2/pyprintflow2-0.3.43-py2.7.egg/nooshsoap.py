'''
Created on Nov 5, 2013

@author: "Colin Manning"
'''

import cgi
import urllib

def createNooshSOAPMessage(noosh_soap_api, body):
    message = '''
    <SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:SOAP-XML="http://xml.apache.org/xml-soap"
        xmlns:noosh="Noosh">
'''
    message += '''
    <SOAP-ENV:Header>
        <authentication domain="%s" identity="%s" sharedPassword="%s"></authentication>
    </SOAP-ENV:Header>
''' % (noosh_soap_api['domain'], noosh_soap_api['identity'], noosh_soap_api['sharedPassword'])

    message += body
    
    message += '</SOAP-ENV:Envelope>'

    return message

def createRemoteFileUploadBody(noosh_soap_api, upload_by, project_id, file_name, file_url):
    file_url_bits = file_url.split('?')
    encoded_file_url = file_url_bits[0]
    if len(file_url_bits) == 2:
        query_params = {}
        query_bits = file_url_bits[1].split('&')
        for query_bit in query_bits:
            p = query_bit.split('=')
            query_params[p[0]] = p[1]
        encoded_file_url += '?' + urllib.urlencode(query_params)
    return '''
    <SOAP-ENV:Body>
        <attachRemoteFile xmlns="DocumentService">
            <creator xsi:type="noosh:ServiceEntity">
                <domain xsi:type="xsd:string">%s</domain>
                <identity xsi:type="xsd:string">%s</identity>
            </creator>
            <prjId xsi:type="xsd:long">%s</prjId>
            <fileTitle xsi:type="xsd:string">%s</fileTitle>
            <remoteFileURI xsi:type="xsd:string">%s</remoteFileURI>
            <isPublic xsi:type="xsd:boolean">true</isPublic>
        </attachRemoteFile>
    </SOAP-ENV:Body>
''' % (noosh_soap_api['domain'], upload_by, project_id, file_name, cgi.escape(encoded_file_url))

