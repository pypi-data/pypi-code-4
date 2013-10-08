# -*- coding: utf-8 -*-
import models as mymodels
import utils
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

class IsModerator(object):

    def process_view(self, request,view_func,view_args,view_kwargs):

        """
        Debug time: Aquí paramos el código para ver las variables de entorno
                    que nos encontramos, tenemos varias opciones:
                    l - Nos muestra el número de linea en la que estamos
                    n - Salta a la siguiente linea de ejecución
                    p dir(var) - Muestra todos los métodos de la variable dir
                    var - Es como hacer un "print" de la variable, muestra su
                          contenido.
        """
        #import pdb; pdb.set_trace()

        """ Devuelve True o False """

        #print request
        #print request.user
        #print view_func.__name__
        #print view_kwargs['slug']
        #print view_kwargs

        # request.user: AnonymousUser
        # view_func.__name__: TopicDelete
        # view_kwargs: {'topicslug': u'primer-partido-20132014-lugo-numancia'}
        # [20/Aug/2013 12:55:27] "GET /foro-cdlugo/delete-topic/primer-partido-20132014-lugo-numancia/ HTTP/1.1" 302 0

        functionlist = ['PostUpdate', 'PostDelete', 'TopicAction', 'TopicDelete']

        try:
            if view_func.__name__ in functionlist:

                if view_kwargs['topicslug'] and view_func.__name__ == 'TopicDelete':
                    if utils.es_moderador(request.user, view_kwargs['topicslug']):
                        return None
                    else:
                        messages.add_message(request, messages.ERROR, _('No puedes eliminar un topic si no eres moderador o admin.'))
                        return redirect('account_profile')

                if view_kwargs['topicslug'] and view_kwargs['id'] and (view_func.__name__ == 'PostUpdate' or view_func.__name__ == 'PostDelete'):
                    if utils.es_suyo(request.user, view_kwargs['id']):
                        return None
                    else:
                        messages.add_message(request, messages.ERROR, _('No puedes editar o eliminar un post que no es tuyo.'))
                        return redirect('account_profile')

                    if utils.es_moderador(request.user, view_kwargs['topicslug']):
                        return None
                    else:
                        messages.add_message(request, messages.ERROR, _('No eres moderador, cuidado con lo que haces.'))
                        return redirect('account_profile')
        except:
            return None

        return None
