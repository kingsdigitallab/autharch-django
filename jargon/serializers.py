from rest_framework import serializers

from .models import (
    EntityRelationType, EntityType, PublicationStatus, MaintenanceStatus,
    ReferenceSource, Repository, ResourceRelationType)


class JargonSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created', 'modified']


class EntityRelationTypeSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = EntityRelationType


class EntityTypeSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = EntityType


class PublicationStatusSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = PublicationStatus


class MaintenanceStatusSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = MaintenanceStatus


class ReferenceSourceSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = ReferenceSource


class RepositorySerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = Repository


class ResourceRelationTypeSerializer(JargonSerializer):
    class Meta(JargonSerializer.Meta):
        model = ResourceRelationType
