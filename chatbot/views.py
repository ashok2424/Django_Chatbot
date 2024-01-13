from django.shortcuts import render , redirect
from django.http import JsonResponse

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from openai import OpenAI
from dotenv import load_dotenv
import os
# Load environment variables from the .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment variable
openai_key = os.getenv("OPENAI_API_KEY")

session_memory = []  # Initialize a list to store conversation history

MAX_MEMORY_SIZE = 2  # Maximum number of pairs of previous user&bot messages  to remember in the session

def ask_openai(message):
    global session_memory  # Access the global session memory

    # Create the OpenAI client with the API key
    client = OpenAI(api_key=openai_key)

    # Include past messages in the prompt for context
    messages = session_memory + [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message},
    ]

    # Generate response from OpenAI with memory context
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=50
    )

    answer = response.choices[0].message.content.strip()

    # Update session memory with the latest message and response
    session_memory.append({"role": "user", "content": message})
    session_memory.append({"role": "system", "content": answer})

    # session_memory = session_memory[-MAX_MEMORY_SIZE:]

    if len(session_memory) > 2*MAX_MEMORY_SIZE:
        session_memory.pop(0)
        session_memory.pop(0)

    # print(len(session_memory))
    # print(session_memory)

    return answer

# Create your views here.
@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html',{'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
        
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')


