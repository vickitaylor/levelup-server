"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status

from levelupapi.models import Game, Gamer, GameType


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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET request for all games in the database
        - using Q to search for games that start with a search term, could also use contains
        this only searches the title and maker columns.

        Returns:
            Response: JSON serialized list of games
        """
        # no longer needed since using annotate below
        # games = Game.objects.all()

        # check to see if there is a query in the url for game_type, then filter to
        # match the id in the query
        game_type = request.query_params.get('type', None)

        search = self.request.query_params.get('search', None)
        gamer = Gamer.objects.get(user=request.auth.user)

        # counting the events per game
        games = Game.objects.annotate(
            event_count=Count('events'),
            user_event_count=Count(
                'events',
                filter=Q(events__organizer=gamer)
            )
        )

        if game_type is not None:
            games = games.filter(game_type_id=game_type)
        if search is not None:
            games = games.filter(
                Q(title__startswith=search) |
                Q(maker__startswith=search)
            )

        serializer = GameSerializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def create(self, request):
    #     """Handle POST operations
    #     Inside the method, the first line is getting the gamer that is logged in. Since all of
    #     our postman or fetch requests have the user???s auth token in the headers, the request
    #     will get the user object based on that token. From there, we use the request.auth.user
    #     to get the Gamer object based on the user.
    #     Then the gameType object is retrieved from the database, so that the type selected is
    #     in the database, and not something new.  That data is passed in from the client and held
    #     in request.data dictionary, the keys must match.
    #     Then to add the game to the database, the create method is called and the fields are
    #     passed as parameters to the function. Once create has ran, it created a new game
    #     instance and id, and then it is being serialized and returned to the client.
    #     - this method that is commented out was the initial create, another create was made to
    #     include validation.

    #     Returns:
    #         Response -- JSON serialized game instance
    #     """
    #     gamer = Gamer.objects.get(user=request.auth.user)
    #     game_type = GameType.objects.get(pk=request.data["game_type"])

    #     game = Game.objects.create(
    #         title=request.data["title"],
    #         maker=request.data["maker"],
    #         number_of_players=request.data["number_of_players"],
    #         skill_level=request.data["skill_level"],
    #         gamer=gamer,
    #         game_type=game_type
    #     )
    #     serializer = GameSerializer(game)
    #     # need to specify the response status code, otherwise it defaults to a 200
    #     return Response(serializer.data, status= status.HTTP_201_CREATED)

    def create(self, request):
        """
        Handle POST operations, has a validation, to ensure the user inputted data that was expected.
        In the above create, each field received data in a new instance of the Game model,
        in the below, the request.data dictionary is passed to the create game serializer as the
        data, and the keys on the dictionary must match the fields on the serializer instance.
        is_valid is used to make sure teh client sent valid data, if true then it is saved.

        Returns:
            Response -- JSON serialized game instance
        """

        gamer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(gamer=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game

        Args:
            request (dict)): holds the information for the request from the client
            pk (int): the primary key of the game object being updated

        Returns:
            Response: Empty body with 204 status code
        """

        # getting the game object requested by the primary key
        game = Game.objects.get(pk=pk)
        # setting fields on game to the values coming in from the client
        game.title = request.data["title"]
        game.maker = request.data["maker"]
        game.number_of_players = request.data["number_of_players"]
        game.skill_level = request.data["skill_level"]

        # created the game_type variable to find the game_type that matched the requested data
        game_type = GameType.objects.get(pk=request.data["game_type"])
        # then assigned game_type to the game variable
        game.game_type = game_type

        # saving to the database
        game.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, response, pk):
        """Handles the DELETE request for a game
        """
        # created a game variable to match the game requested to the one from the list
        game = Game.objects.get(pk=pk)
        # deletes the game from the database
        game.delete()
        # a response is not received, and when competed it will return code 204
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    """
    # *** remember to add the new fields created with annotate, so that it can be used by
    # the serializer since they are not on the model. ***
    event_count = serializers.IntegerField(default=None)
    user_event_count = serializers.IntegerField(default=None)

    class Meta:
        model = Game
        # for the fields you specify what you want returned (if it is not specified, you will
        # not get it back, ie, if id was not included, you cannot access the # event.id property)
        fields = ('id', 'game_type', 'title', 'maker',
                  'gamer', 'number_of_players', 'skill_level', 'event_count', 'user_event_count'
                  )
        depth = 1


class CreateGameSerializer(serializers.ModelSerializer):
    """ serializer for create game, to validate inputs on create game
    """
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker',
                  'number_of_players', 'skill_level', 'game_type']
