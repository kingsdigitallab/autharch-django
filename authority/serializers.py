from geonames_place.serializers import \
    PlaceSerializer as GeonamesPlaceSerializer
from jargon.serializers import EntityTypeSerializer
from rest_framework import serializers

from .models import (
    BiographyHistory, Description, Entity, Identity, LanguageScript,
    NameEntry, Place
)


class BiographyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiographyHistory
        fields = ['abstract', 'content', 'sources', 'copyright']
        depth = 10


class PlaceSerializer(serializers.ModelSerializer):
    place = GeonamesPlaceSerializer(many=False, read_only=True)

    class Meta:
        model = Place
        fields = ['place', 'address', 'role']
        depth = 10


class LanguageScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageScript
        fields = ['language', 'script']
        depth = 10


class DescriptionSerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)
    languages_scripts = LanguageScriptSerializer(many=True, read_only=True)
    biography_history = BiographyHistorySerializer(read_only=True)

    class Meta:
        model = Description
        fields = ['function', 'structure_or_genealogy',
                  'places', 'languages_scripts', 'biography_history']
        depth = 10


class NameEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NameEntry
        fields = ['display_name', 'authorised_form', 'date_from', 'date_to']


class IdentitySerializer(serializers.ModelSerializer):
    name_entries = NameEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Identity
        fields = ['preferred_identity', 'name_entries', 'date_from', 'date_to']
        depth = 10


class EntitySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entity-detail', lookup_field='pk'
    )

    entity_type = EntityTypeSerializer(many=False, read_only=True)
    identities = IdentitySerializer(many=True, read_only=True)
    descriptions = DescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Entity
        fields = ['id', 'url', 'display_name', 'entity_type',
                  'identities', 'descriptions', ]
        depth = 10
