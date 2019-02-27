from rest_framework import serializers

from .models import PublicationStatus, Repository, ReferenceSource


class PublicationStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicationStatus
        fields = '__all__'


class ReferenceSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReferenceSource
        fields = '__all__'


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'
