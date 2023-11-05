from django.db import models
import uuid


# Create your models here.

class Room(models.Model):
    room_code = models.CharField(max_length=11)
    name = models.CharField(max_length=50)

    def generate_unique_room_code(self):
        while True:
            room_code = f'{uuid.uuid4().hex[:5]}-{uuid.uuid4().hex[:5]}'
            if not Room.objects.filter(room_code=room_code).exists():
                return room_code

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = self.generate_unique_room_code()
        super().save(*args, **kwargs)
