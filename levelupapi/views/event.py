"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event


class EventView(ViewSet):
    """Level up events view
    """

    def retrieve(self, request, pk):
        """Handles the GET requests for a single event

        Args:
            pk (int): the primary key for the event

        Returns:
            Response -- JSON serialized game type
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET requests for all events in the database

        Returns:
            Response -- JSON serialized list of events
        """
        events = Event.objects.all()
        
        # adding query for game id to the events url
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events.
    """
    class Meta:
        model = Event
        fields = ('game', 'description', 'date', 'time', 'organizer', 'attendees')
        # depth added for embed details, depth =1, gives details on the foreign keys (game,
        # organizer, attendees) when changed to 2, it embedded details from the foreign
        # keys for the organizer and attendees and game (but not gamer, that would be a
        # depth of 3).
        depth = 2
