from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import SpyCat, Mission, Target
from .serializers import SpyCatSerializer, MissionSerializer, TargetSerializer


class SpyCatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Spy Cats.
    """

    queryset = SpyCat.objects.all()
    serializer_class = SpyCatSerializer

    @action(detail=True, methods=["post"])
    def assign_mission(self, request, pk=None):
        """
        Assign a mission to a spy cat.
        """
        spy_cat = self.get_object()
        mission_id = request.data.get("mission_id")
        try:
            mission = Mission.objects.get(id=mission_id, cat__isnull=True)
            mission.cat = spy_cat
            mission.save()
            return Response(
                {"message": "Mission assigned successfully."},
                status=status.HTTP_200_OK,
            )
        except Mission.DoesNotExist:
            return Response(
                {"error": "Mission not available for assignment."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Missions and their Targets.
    """

    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of assigned missions.
        """
        mission = self.get_object()
        if mission.cat:
            return Response(
                {
                    "error": "Cannot delete a mission"
                    "that is assigned to a spy cat."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Mark a mission as completed.
        """
        mission = self.get_object()
        if not all(target.is_complete for target in mission.targets.all()):
            return Response(
                {
                    "error": "All targets must be completed before"
                    "marking the mission as completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        mission.is_complete = True
        mission.save()
        return Response(
            {"message": "Mission marked as completed."},
            status=status.HTTP_200_OK,
        )


class TargetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual Targets.
    """

    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def update(self, request, *args, **kwargs):
        """
        Prevent updates to Notes or Targets if marked as complete.
        """
        target = self.get_object()
        if target.is_complete:
            return Response(
                {"error": "Cannot update a completed target."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if target.mission.is_complete:
            return Response(
                {"error": "Cannot update a target in a completed mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def mark_complete(self, request, pk=None):
        """
        Mark a target as completed.
        """
        target = self.get_object()
        target.is_complete = True
        target.save()
        return Response(
            {"message": "Target marked as completed."},
            status=status.HTTP_200_OK,
        )
