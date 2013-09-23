#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
import logging
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
# from django.utils.translation import ugettext as _
from django.views.generic import View
# from django.contrib.auth.models import User
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import FormLogin

log = logging.getLogger('django')


class Login(View):
    def post(self, request):
        """
        Login: post
        -----------

        Used to try to login the user with given credentials.

        :param request:
        :return: HttpResponse
        """
        form = FormLogin(request.POST)
        if form.is_valid():
            # let's test if user can authenticate, user must be registered in users data table
            usuario = authenticate(username=form.data['username'], password=form.data['password'])
            if usuario is not None and usuario.is_active:
                login(request=request, user=usuario)
                try:
                    next_url = request.GET['next']
                except Exception, e:
                    next_url = settings.LOGIN_REDIRECT_URL

                return HttpResponseRedirect(next_url)
            else:
                form.errors[u'Autenticação'] = u'Usuário e/ou senha incorretos'

        return render(request, u'django_users_login/login.html', {u'form': form})

    def get(self, request):
        form = FormLogin()
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        return render(request, u'django_users_login/login.html', {u'form': form})


class Logout(View):
    """
    Logout
    ======

    Logout view to get it out with the user.

    """

    def get(self, request):
        logout(request=request)
        return redirect(to=settings.LOGIN_REDIRECT_URL)


class ForgotPassword(View):
    def get(self, request):
        return render(request, 'django_users_login/forgot_password.html')


class Profile(View):
    """
    Profile
    =======

    View for profile data

    """

    def post(self, request):
        return render(request, u'core/index.html')

    def get(self, request):
        return render(request, u'core/index.html')


class SignUp(View):
    def post(self, request):
        form = FormLogin(request.POST)
        if form.is_valid():
            if request.is_ajax():
                pass
            else:
                pass

        return render(request, 'signup.html')

    def get(self, request):
        return HttpResponse('Not implemented yet.')
        # if SIGN_UP_MODE:
        #     return render(request, 'signup.html')
        # else:
        #     return HttpResponseForbidden(_('operation not permitted'))


        # class Manage(View):
        #     """
        #     Manage
        #     ======
        #
        #     This class has all methods to manage users. You can edit, delete, create and update all users.
        #
        #     """
        #
        #     task = None
        #
        #     def suspend_user(self, request, id):
        #         pass
        #
        #     def reset_password_user(self, request, id):
        #         pass
        #
        #     def edit_user(self, request, id):
        #         pass
        #
        #     def delete_user(self, request, id):
        #         pass
        #
        #     def create_user(self, request, id):
        #         pass
        #
        #     def post(self, request):
        #         self.get(request)
        #
        #     def put(self, request):
        #         pass
        #
        #     def get(self, request, method, id=None):
        #         try:
        #             getattr(self, self.task)(request, id) # this mapping all requests to this class
        #         except Exception as e:
        #             pass
        #
        #
        # # class ListUsers(View):
        # #     """
        # #     ListUsers
        # #     =========
        # #
        # #     List all users to manage them.
        # #
        # #     """
        # #
        # #     def get(self, request):
        # #
        # #         contact_list = User.objects.all()
        # #         paginator = Paginator(contact_list, USERS_PER_PAGE)
        # #
        # #         page = request.GET.get('page')
        # #         try:
        # #             users = paginator.page(page)
        # #         except PageNotAnInteger:
        # #             # If page is not an integer, deliver first page.
        # #             users = paginator.page(1)
        # #         except EmptyPage:
        # #             # If page is out of range (e.g. 9999), deliver last page of results.
        # #             users = paginator.page(paginator.num_pages)
        # #
        # #         return render_to_response('django_users_login/list.html', {"users": users})
        # #
        # #         # def dispatch(self, request, *args, **kwargs):
        # #         #     """
        # #         #     dispach
        # #         #     -------
        # #
        # #         #     If the current user is not admin then
        # #         #     """
        # #
        # #         #     if request.user.is_authenticated():
        # #         #         return super(ListUsers, self).dispatch(request, *args, **kwargs)