#!/usr/bin/python
#coding=utf-8

import config
import time
import utils
import bottle
from bottle import request
from lxml import etree
from hashlib import sha1
from logger import logger

app = bottle.Bottle()


@app.route('/', method=["GET", "POST"])
def weixin():
    '''weixin robot'''
    if request.method == "POST":

        try:
            rxml = etree.XML(request.body.read())
        except:
            logger.error("not valid xml")
            return ''

        try:
            FromUser = rxml.xpath('FromUserName')[0]
            ToUser = rxml.xpath('ToUserName')[0]
            FromUser.text, ToUser.text = ToUser.text, FromUser.text
        except IndexError:
            logger.error("FromUserName or ToUserName missing")
            return ''

        try:
            MsgType = rxml.xpath('MsgType')[0]
            msg_type = MsgType.text
            MsgType.text = 'text'
        except IndexError:
            logger.error("MsgType missing")
            return ''

        timestamp = str(int(time.time()))
        etree.SubElement(rxml, "CreateTime").text = etree.CDATA(timestamp)
        etree.SubElement(rxml, 'FuncFlag').text = etree.CDATA('0')

        if rxml.xpath('Content'):
            Content = rxml.xpath('Content')[0]
        else:
            Content = etree.SubElement(rxml, 'Content')

        if msg_type == 'text':
            req_content = Content.text.strip()
            logger.info('%s-%s' % (ToUser.text, req_content))
            try:
                content = utils.func(req_content)
            except Exception, e:
                logger.error(e)
                content = config.EXCEPTION_RES
            Content.text = content
        elif msg_type == 'event':
            try:
                event = rxml.xpath('Event')[0].text
                logger.info('%s-%s' % (ToUser.text, event))
            except IndexError:
                logger.error("Event missing")
                return ''
            if event == 'subscribe':
                content = config.SUB_RES
            elif event == 'unsubscribe':
                content = config.UNSUB_RES
            else:
                content = config.DEFAULT_RES
            Content.text = etree.CDATA(content)
        elif msg_type == 'link':
            Content.text = etree.CDATA(config.DEFAULT_RES)
        elif msg_type == 'image':
            Content.text = etree.CDATA(config.DEFAULT_RES)
        elif msg_type == 'location':
            Content.text = etree.CDATA(config.DEFAULT_RES)
        else:
            Content.text = etree.CDATA(config.DEFAULT_RES)
        response = etree.tostring(rxml, encoding=unicode)
        return response
    else:
        token = config.TOKEN
        signature = request.params.get('signature', '')
        timestamp = request.params.get('timestamp', '')
        nonce = request.params.get('nonce', '')
        echostr = request.params.get('echostr', '')
        hashstr = sha1(''.join(sorted([token, timestamp, nonce]))).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            return ''

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True)
