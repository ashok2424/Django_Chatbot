# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username}: {self.message}'
    

    


# For calling above function in views  we can use below piece of code and render if needed
    
# from .models import Chat

# def some_view(request):
#     chat_instance = Chat.objects.get(pk=1)
#     string_representation = str(chat_instance)
#     return render(request, 'some_template.html', {'string_representation': string_representation})
