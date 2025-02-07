from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render,redirect
from django.views.generic import View,ListView,TemplateView
import datetime
from .set_online_middleware import *

from .forms import *
from .models import Chat,Message
from django.db.models import Q
from celleryworker.tasks import send_bulk_message_task


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

        contact_status = {}
        user = self.request.user

        for chat in self.object_list:
            if chat.first_user == user:
                contact_status[chat] = {
                    'is_online': is_user_online(chat.second_user.id),
                    'user': chat.second_user,
                    'chat_id': chat.id,
                    'last_message': chat.last_message,
                    'user_object': get_user_model().objects.get(username=chat.second_user),
                }
            else:
                contact_status[chat] = {
                    'is_online': is_user_online(chat.first_user_id),
                    'user': chat.first_user,
                    'chat_id': chat.id,
                    'last_message': chat.last_message,
                    'user_object': get_user_model().objects.get(username=chat.first_user),
                }

        context['user'] = user
        context['chat_list_map'] = contact_status

        return context



class SearchView(LoginRequiredMixin,ListView):
    template_name = 'messenger/search.html'
    model = get_user_model()
    paginate_by = 20
    form_class = SearchForm
    context_object_name = 'users'

    def __init__(self,*args,**kwargs):
        self.is_filter = kwargs.pop('is_filter',False)
        super().__init__(*args,**kwargs)


    def get_queryset(self):
        query_set = get_user_model().objects.all().exclude(id=self.request.user.id)
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
        form = MessageSendForm()
        try:
            receiver = get_user_model().objects.get(username=nick)
        except get_user_model().DoesNotExist:
            raise Http404("User not found")

        chat_list = Chat.objects.filter((Q(first_user=user) | Q(second_user=user)) &Q(last_message__isnull=False)).order_by('-last_changes')

        chat_between = Chat.objects.filter((Q(first_user=user) | Q(second_user=user)) & (Q(first_user=receiver) | Q(second_user=receiver))).first()
        messages = Message.objects.filter(chat=chat_between)


        is_online = is_user_online(chat_between.second_user.id if chat_between.first_user == user else chat_between.first_user.id)

        contact_status = {}


        for chat in chat_list:
            if chat.first_user == user:
                contact_status[chat] = {
                    'is_online': is_user_online(chat.second_user.id),
                    'user': chat.second_user,
                    'chat_id': chat.id,
                    'last_message': chat.last_message,
                    'user_object': get_user_model().objects.get(username=chat.second_user),
                }
            else:
                contact_status[chat] = {
                    'is_online': is_user_online(chat.first_user_id),
                    'user': chat.first_user,
                    'chat_id': chat.id,
                    'last_message': chat.last_message,
                    'user_object': get_user_model().objects.get(username=chat.first_user),
                }


        context = {
            'chat_list_map': contact_status,
            'user': user,
            'messages': messages,
            'nick': nick,
            'chat_id': chat_id,
            'chat_between': chat_between,
            'form': form,
            'is_online': is_online,
        }
        return render(request, self.template_name, context)



@login_required
def add_user_to_chat(request, name):
    user = request.user

    try:
        nick_user = get_user_model().objects.get(username=name)
    except get_user_model().DoesNotExist:
        raise Http404("User not found")

    user_check = Chat.objects.filter(
        (Q(first_user=user) & Q(second_user=nick_user)) |
        (Q(second_user=user) & Q(first_user=nick_user))
    ).first()

    if user_check:
        return redirect('chat', chat_id=user_check.id, nick=name)
    else:
        new_chat = Chat.objects.create(first_user=user, second_user=nick_user)
        return redirect('chat', chat_id=new_chat.id, nick=name)



class ProfileView(LoginRequiredMixin,View):
    template_name = 'messenger/profile.html'


    def get(self, request,name):
        user = request.user
        context = {
            'user': user,
        }
        return render(request, self.template_name, context)


class EditProfile(LoginRequiredMixin,View):
    template_name = 'messenger/editprofile.html'

    def get(self, request,name):
        user = request.user
        context = {
            'user': user,
        }
        return render(request, self.template_name,context)


    def post(self,request,name):
        user = request.user
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        photo = request.FILES.get('photo', None)

        if get_user_model().objects.filter(username=username).exclude(id=user.id).exists():
            return redirect('profile', name)
        else:
            user_update = get_user_model().objects.get(username=user.username)
            user_update.first_name = first_name
            user_update.last_name = last_name
            if photo:
                user_update.photo = photo

            user_update.username = username

            user_update.save()


        return redirect('profile',name)


class UserProfileView(View):
    template_name = 'messenger/userprofile.html'

    def get(self, request, name):
        user = request.user

        user_object = get_user_model().objects.get(username=name)

        is_online = is_user_online(user_object.id)

        context = {
            'user': user,
            'user_object': user_object,
            'is_online': is_online,
        }


        return render(request, self.template_name,context)


class MessageEmailSendVIew(LoginRequiredMixin,View):
    template_name = 'messenger/email_send.html'
    def get(self, request):
        user = request.user
        if not user.is_staff:
            return redirect('index')

        return render(self.request, self.template_name, {'user': user})

    def post(self,request):
        message = request.POST['email_message']

        all_users_email = get_user_model().objects.all()

        all_emails = []

        for all_user in all_users_email:
            all_emails.append(all_user.email)

        send_bulk_message_task.delay(all_emails, message)

        return redirect('index')


