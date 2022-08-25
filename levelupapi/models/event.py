from django.db import models

# for the many to many add the userIds to an array for attendees on the json file.

class Event(models.Model):
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="events")
    description = models.TextField(max_length=150)
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    organizer = models.ForeignKey("Gamer", on_delete=models.CASCADE, related_name="event")
    attendees = models.ManyToManyField("Gamer", through="EventGamer", related_name="events")

    @property #the getter
    def joined(self):
        return self.__joined

    @joined.setter #the setter
    def joined(self, value):
        self.__joined = value
