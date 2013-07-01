import os

def dbopen_handler(event):
    if os.environ.get("RPDB2_ENABLE", "false").lower() == "true":
        import rpdb2
        passwd = os.environ.get("RPDB2_PASSWD", "passwd")
        rpdb2.start_embedded_debugger(passwd, timeout=0)
