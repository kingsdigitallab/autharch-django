from rest_framework import serializers

from .models import EntityType, PublicationStatus, ReferenceSource, Repository


class JargonSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created', 'modified']


class EntityTypeSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = EntityType


class PublicationStatusSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = PublicationStatus


class ReferenceSourceSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = ReferenceSource


class RepositorySerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = Repository
