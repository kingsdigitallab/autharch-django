from jargon.serializers import EntityTypeSerializer
from rest_framework import serializers

from .models import Entity, Identity, NameEntry


class NameEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NameEntry
        fields = ['display_name', 'authorised_form']


class IdentitySerializer(serializers.ModelSerializer):
    name_entries = NameEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Identity
        fields = ['preferred_identity', 'name_entries']
        depth = 10


class EntitySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entity-detail', lookup_field='pk'
    )

    entity_type = EntityTypeSerializer(many=False, read_only=True)
    identities = IdentitySerializer(many=True, read_only=True)

    class Meta:
        model = Entity
        fields = ['id', 'url', 'display_name', 'entity_type',
                  'identities', 'descriptions']
        depth = 10
