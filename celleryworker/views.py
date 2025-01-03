from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render,redirect
from django.views.generic import View,ListView,TemplateView
import datetime

from .forms import SearchForm
from .models import Chat,Message
from django.db.models import Q
from django.contrib.auth.models import User

class IndexView(LoginRequiredMixin,ListView):
    template_name = 'messenger/chatInactive.html'
    model = Chat
    ordering = '-last_changes'
    context_object_name = 'user_chats'


    def get_queryset(self):
        user = self.request.user

        query_set = Chat.objects.filter(Q(first_user = user) | Q(second_user = user)).order_by('-last_changes')

        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user'] = self.request.user

        return context



class SearchView(LoginRequiredMixin,ListView):
    template_name = 'messenger/search.html'
    model = User
    paginate_by = 20
    form_class = SearchForm
    context_object_name = 'users'

    def __init__(self,*args,**kwargs):
        self.is_filter = kwargs.pop('is_filter',False)
        super().__init__(*args,**kwargs)


    def get_queryset(self):
        query_set = User.objects.all().exclude(id=self.request.user.id)
        form = SearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data['username']

            if query:
                query_set = query_set.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
                self.is_filter = True

        return query_set


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['search_user'] = SearchForm(self.request.GET or None)
        context['is_filter'] = self.is_filter

        return context


class Message_view(LoginRequiredMixin,View):
    template_name = 'messenger/chatActive.html'

    def get(self, request,chat_id,nick):
        user = self.request.user

        try:
            receiver = User.objects.get(username=nick)
        except User.DoesNotExist:
            raise Http404("User not found")

        chat_list = Chat.objects.filter(Q(first_user = user) | Q(second_user = user)).order_by('-last_changes')

        chat_between = Chat.objects.filter((Q(first_user = user) | Q(second_user = user)) & (Q(first_user=receiver) | Q(second_user = receiver))).first()
        messages = Message.objects.filter(chat_id=chat_between)
        context = {
            'chat': chat_list,
            'user': user,
            'messages': messages,
            'nick': nick,
            'chat_id': chat_id,
            'chat_between': chat_between,
        }
        return render(request, self.template_name,context)

    def post(self, request,chat_id,nick):
        message= self.request.POST['message']
        user = self.request.user

        try:
            receiver = User.objects.get(username=nick)
        except User.DoesNotExist:
            raise Http404("User not found")

        chat = Chat.objects.filter((Q(first_user = user) | Q(second_user = user)) & (Q(first_user=receiver) | Q(second_user = receiver))).first()

        chat.last_message = message
        chat.last_changes = datetime.datetime.now()

        chat.save(update_fields=['last_message','last_changes'])

        Message.objects.create(sender=user,receiver=receiver,text=message,chat_id=chat_id)

        return redirect('chat',chat_id,nick)







