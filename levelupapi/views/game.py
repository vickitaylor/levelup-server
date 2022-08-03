"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Game

class GameView(ViewSet):
    """Level up games view
    """

    def retrieve(self, request, pk):
        """Handles the GET request for a single game

        Args:
            request (dict): The request from the method parameters holds all the information
            for the request from the client. The request.query_params is a dictionary of any
            query parameters that were in the url. If the 'type' key is not present on the
            dictionary it will return None.
            pk (int): the primary key for the game

        Returns:
            response -- JSON serializers game for the selected key
        """
        try:
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET request for all games in the database

        Returns:
            Response: JSON serialized list of games
        """
        games = Game.objects.all()

        # check to see if there is a query in the url for game_type, then filter to
        # match the id in the query
        game_type = request.query_params.get('type', None)
        if game_type is not None:
            games = games.filter(game_type_id=game_type)

        serializer =  GameSerializer(games, many=True)
        return Response(serializer.data)

class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    """
    class Meta:
        model = Game
        fields = ('game_type', 'title', 'maker', 'gamer', 'number_of_players', 'skill_level')
        depth = 1
