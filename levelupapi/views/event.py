"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer


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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handles the GET requests for all events in the database

        Returns:
            Response -- JSON serialized list of events
        """
        # events = Event.objects.all()
        events = Event.objects.annotate(attendees_count=Count('attendees'))

        # adding query for game id to the events url
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)

        gamer = Gamer.objects.get(user=request.auth.user)

        # Set the 'joined' property on every event
        for event in events:
            # check to see if the gamer is in the attendees list on the event, this will
            # evaluate to true of false if the gamer is in the attendees list
            event.joined = gamer in event.attendees.all()

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handles the POST operations

        Returns:
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data["game"])

        event = Event.objects.create(
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            game=game,
            organizer=gamer
        )
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handles the PUT requests for an event

        Returns:
            Response: Empty body with 204 status code
        """
        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]

        game = Game.objects.get(pk=request.data["game"])
        event.game = game

        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, response, pk):
        """Handles the DELETE request for an event
        """
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    # the action decorator, turns the method into a new route, the below will accept a POST method
    # because of the detail=True, the url will include the primary key. We need to know the event
    # the user signs up for, and need the pk for that. The route is named after the function

    @action(methods=['POST'], detail=True)
    def signup(self, request, pk):
        """POST request for a user to sign up for an event
        """
        # getting the gamer who is logged in and event object by its primary key
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)

        # adding the gamer variable to the event as an attendee.  Since the many to many field,
        # attendees, is on the event model. the add() method creates the relationship between
        # the event and the gamer by adding the event_id and the gamer_id to the join table
        # then a 201 response is sent back
        event.attendees.add(gamer)
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=True)
    def leave(self, request, pk):
        """DELETE request for a user to sign up for an event
        """
        # getting the gamer who is logged in and event object by its primary key
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)

        event.attendees.remove(gamer)
        return Response({'message': 'Gamer removed'}, status=status.HTTP_204_NO_CONTENT)


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events.
    """
    attendees_count = serializers.IntegerField(default=None)

    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date',
                  'time', 'organizer', 'attendees', 'joined', 'attendees_count')
        # depth added for embed details, depth =1, gives details on the foreign keys (game,
        # organizer, attendees) when changed to 2, it embedded details from the foreign
        # keys for the organizer and attendees and game (but not gamer, that would be a
        # depth of 3).
        depth = 2
