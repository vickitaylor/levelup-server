from django.db import models

# no need to use related name here since it is a many to many table

class EventGamer(models.Model):
    gamer = models.ForeignKey("Gamer", on_delete=models.CASCADE)
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
