from django.db import models


class Game(models.Model):
    game_type = models.ForeignKey("GameType", on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    maker = models.CharField(max_length=55)
    gamer = models.ForeignKey("Gamer", on_delete=models.CASCADE)
    number_of_players = models.PositiveIntegerField(default=0)
    skill_level = models.PositiveIntegerField(default=0)
