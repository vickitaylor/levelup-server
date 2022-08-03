"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import GameType


class GameTypeView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type.
        Using the retrieve method gests a single object based on the primary key, the serializer
        converts the data to JSON.  After getting the object it is passed to the serializer,
        and then serializer.data is passed to the Response as the response body.  (Response
        combines _set_headers and wfile.write functions, used prior.)

        Returns:
            Response -- JSON serialized game type
        """
        # added try/ except to display not found message when a id is not valid
        try:
            game_type = GameType.objects.get(pk=pk)
            serializer = GameTypeSerializer(game_type)
            return Response(serializer.data)
        except GameType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to get all game types from the database. game_types is now a list
        of all of the GameType objects, passed to the serializer, many=True is added to let
        the serializer know that a list rather than a single object is being serialized

        Returns:
            Response -- JSON serialized list of game types
        """
        game_types = GameType.objects.all()
        serializer = GameTypeSerializer(game_types, many=True)
        return Response(serializer.data)

class GameTypeSerializer(serializers.ModelSerializer):
    """JSON serializer for game types.
    The Meta class holds the configuration for the serializer.  This is telling the serializer
    to use the GameType model and to include the id and label fields
    """
    class Meta:
        model = GameType
        fields = ('id', 'label')
