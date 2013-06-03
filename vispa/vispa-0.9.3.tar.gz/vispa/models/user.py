# -*- coding: utf-8 -*-

# imports
import time, random, smtplib, os
from hashlib import sha256
from sqlalchemy import Column
from sqlalchemy.types import Unicode, DateTime, Integer
from datetime import datetime
import cherrypy
import vispa
from vispa.models import Base

class User(Base):

    INACTIVE = 0
    ACTIVE = 1
    MAX_USERS   = 500
    PW_LENGTH   = [8, 64]
    NAME_LENGTH = [6, 30]
    NAME_CHARS  = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890_-+'
    FORBIDDEN_NAMES = ['data', 'guest', 'global', 'user', 'delete', 'select', 'insert', 'update', 'drop']

    __tablename__ = 'user'
    id            = Column(Integer, nullable=False, primary_key=True)
    name          = Column(Unicode(30), nullable=False, unique=True)
    password      = Column(Unicode(64), nullable=False)
    email         = Column(Unicode(100), nullable=False, unique=True)
    created       = Column(DateTime, nullable=False, default=datetime.now)
    last_request  = Column(DateTime, nullable=False, default=datetime.now)
    status        = Column(Integer, nullable=False, default=ACTIVE)
    hash          = Column(Unicode(100))

    @staticmethod
    def get_by_id(session, id):
        return session.query(User).filter_by(id=id).first()

    @staticmethod
    def get_by_name(session, name):
        return session.query(User).filter_by(name=name).first()

    @staticmethod
    def get_by_email(session, email):
        return session.query(User).filter_by(email=email).first()

    @staticmethod
    def get_by_hash(session, hash):
        return session.query(User).filter_by(hash=hash).first()

    @staticmethod
    def all(session):
        return session.query(User)

    @staticmethod
    def update_last_request(session, id):
        user = User.get_by_id(session, id)
        if user:
            user.last_request = datetime.now()

    @staticmethod
    def is_active(session, id):
        user = User.get_by_id(session, id)
        return user.status == User.ACTIVE

    @staticmethod
    def login(session, username, password):
        if username == None:
            return 'Invalid username'
        if password == None:
            return 'Invalid password'
        
        user = User.get_by_name(session, username)
        
        if user is None:
            user = User.get_by_email(session, username)
            if user is None:
                return 'Unknown user'
        
        if user.password != password:
            return 'Wrong password'
        
        if not User.is_active(session, user.id):
            return "Your account is not active yet"
        
        vispa.fire_callback("user.login", user)

        return user

    @staticmethod
    def register(session, name, email, password):
        # name exists?
        if User.get_by_name(session, name) is not None:
            return 'This username already exists!'
        
        # check the email
        if User.get_by_email(session, email) is not None:
            return 'Your mail address already exists!'
        
        # Max Users ?
        count = session.query(User).count()
        if count >= User.MAX_USERS:
            return 'The maximum number of registered users is reached!'
        
        # check the passwd's
        if len(password) < User.PW_LENGTH[0] or len(password) > User.PW_LENGTH[1]:
            return 'The length of your password should be between %d and %d chars!' % tuple(User.PW_LENGTH)
        
        # email valid?
        email = email.lower()
        valid_hosts = vispa.config('user', 'registration.mail_hosts', [])
        emailvalid = True
        emailparts = email.split("@")
        if len(emailparts) != 2:
            emailvalid = False
        else:
            host = emailparts[1]
            if len(valid_hosts) and host not in valid_hosts:
                emailvalid = False
        if not emailvalid:
            return 'This is not a valid mail address!'
        
        # check the name
        
        # => length
        if len(name) < User.NAME_LENGTH[0] or len(name) > User.NAME_LENGTH[1]:
            return 'The length of the username should be between %d and %d chars!' % tuple(User.NAME_LENGTH)
        
        # => chars
        for char in name:
            if char not in User.NAME_CHARS:
                return 'The char \'%s\' is not allowed!' % char
        
        # name forbidden?
        if name.lower() in User.FORBIDDEN_NAMES:
            return 'This username is forbidden!'
        
        ### The userdata passed all checks
        
        # create a hash
        hash = User.generate_hash(32)
        
        # => register the user
        autoactive = vispa.config('user', 'registration.autoactive', True)
        status = User.ACTIVE if autoactive else User.INACTIVE
        user = User(name=name, password=password, email=email, hash=hash, status=status)
        session.add(user)
        
        # send the registration mail?
        if vispa.config('user', 'registration.sendmail', False):
            User.send_registration_mail(name, email, hash)
        
        # we need a commit this time
        # because we need the id which is
        # generated after the commit
        session.commit()
        
        vispa.fire_callback("user.register", user)

        return user

    @staticmethod
    def send_registration_mail(name, email, hash):
        # create the mail content
        from_addr = "do-not-reply@vispa.physik.rwth-aachen.de"
        to_addr = email
        subject = "Your Vispa Registration"
        
        response_host = vispa.config('user', 'registration.activation', 'http://localhost')
        link = os.path.join(response_host, "?hash=%s" % hash)
        msg = "Hi %s!\n\nTo finish your registration for Vispa, click on the link below:\n\n%s\n\nYour Vispa-Team!" % (name, link)
        
        User.send_mail(from_addr, to_addr, subject, msg)

    @staticmethod
    def send_mail(from_addr, to_addr, subject="", content=""):
        smtp_host = vispa.config('user', 'registration.smtp_host', '127.0.0.1')
        smtp_port = vispa.config('user', 'registration.smtp_port', 25)
        server = smtplib.SMTP(smtp_host, smtp_port)
        
        head = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_addr, to_addr, subject)
        
        server.sendmail(from_addr, to_addr, head+content)

    @staticmethod
    def forgot_password(db, name_or_mail):
        user = User.get_by_name(db, name_or_mail)
        if not isinstance(user, User):
            user = User.get_by_email(db, name_or_mail.lower())
        if not user:
            return False
        elif user.status == User.INACTIVE:
            user.send_registration_mail(user.name, user.email, user.hash)
            return False
        
        hash = User.generate_hash(32)
        user.hash = hash
        
        # create the mail content
        from_addr = "do-not-reply@vispa.physik.rwth-aachen.de"
        to_addr = user.email
        subject = "Your Vispa Password"
        
        response_host = vispa.config('user', 'registration.forgot', 'http://localhost')
        link = os.path.join(response_host, "?hash=%s" % hash)
        msg = "Hi %s!\n\nYou requested a password change.\nClick on the link below to select a new one:\n\n%s\n\nYour Vispa-Team!" % (user.name, link)
        
        try:
            User.send_mail(from_addr, to_addr, subject, msg)
        except:
            pass
        return link

    @staticmethod
    def activate(session, hash):
        user = User.get_by_hash(session, hash)
        if not isinstance(user, User):
            return False
        if User.is_active(session, user.id):
            return False
        user.status = User.ACTIVE
        vispa.fire_callback("user.activate", user)
        return user

    @staticmethod
    def generate_hash(length=10):
        chars = "abcdefghijklmnopqrstuvwxyz"
        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars += "0123456789"
        code = ""
        for i in range(length):
            rnd = int(round(random.uniform(0, len(chars) - 1)))
            code += chars[rnd]
        return code

