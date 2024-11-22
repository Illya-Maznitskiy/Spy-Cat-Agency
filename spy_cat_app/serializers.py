from rest_framework import serializers
from .models import SpyCat, Target, Mission


class SpyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = "__all__"


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = "__all__"


class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = "__all__"

    def create(self, validated_data):
        """
        Create a new Mission and its related Targets from validated data.
        """
        targets_data = validated_data.pop("targets")
        mission = Mission.objects.create(**validated_data)
        for target_data in targets_data:
            Target.objects.create(mission=mission, **target_data)
        return mission

    def update(self, instance, validated_data):
        """
        Update an existing Mission and its related Targets from validated data.
        """
        targets_data = validated_data.pop("targets", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if targets_data:
            instance.targets.all().delete()
            for target_data in targets_data:
                Target.objects.create(mission=instance, **target_data)

        return instance
