from rest_framework import serializers

from .models import PublicationStatus, ReferenceSource, Repository


class JargonSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created', 'modified']


class PublicationStatusSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = PublicationStatus


class ReferenceSourceSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = ReferenceSource


class RepositorySerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = Repository
