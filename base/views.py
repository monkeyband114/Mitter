from multiprocessing import context
from pydoc_data.topics import topics
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserStartForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower() 
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user nor dey')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user) 
            return redirect('home')
        else:
            messages.error(request, 'Omo  password not exit')  
               
    context = {'page': page}
    return render(request, 'base/login_register.html', context)
 

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    page = 'register'
    form = MyUserStartForm()
    
    if request.method == 'POST':
        form = MyUserStartForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)   
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An Error Occurr ed in Registration')
    return render(request, 'base/login_register.html', {'form':form}) 
 
    
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    
    context =  {'rooms': rooms, 'topics': topics, 
                'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk) 
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    # description = room.description.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
            
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
        
    context = {'room': room, 'room_messages':room_messages, 
               'participants':participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms,
               'room_messages': room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login') 
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
        
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context) 

@login_required(login_url='login') 
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('you are not the owner go crate a room')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
             
    context = {'form':form, 'topics':topics, 'room':room }
    return render(request, 'base/room_form.html', context)
    
@login_required(login_url='login') 
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('you are not the owner go crate a room')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
      
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login') 
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('cannot delete not your message')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
      
    return render(request, 'base/delete.html', {'obj':message})



@login_required(login_url='login')
def editUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
            
    context = {'form':form}
    return render(request, 'base/edit_profile.html', context)


def activity(request):
    room_messages = Message.objects.all()
    
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)


def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(Q(name__icontains=q))
    
    return render(request, 'base/topics.html', {'topics':topics})




