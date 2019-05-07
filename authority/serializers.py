from geonames_place.serializers import \
    PlaceSerializer as GeonamesPlaceSerializer
from jargon.serializers import EntityTypeSerializer
from rest_framework import serializers

from .models import (
    BiographyHistory, Description, Entity, Identity, LanguageScript,
    NameEntry, Place, LocalDescription
)

# TODO _ Move this.


def date_format(date_from, date_to):
    if date_from is not None:
        if date_to is not None:
            return "{} - {}".format(date_from, date_to)
        else:
            return "{} - ".format(date_from)
    else:
        if date_to is not None:
            return " - {}".format(date_to)
        else:
            return "Unknown"


class BiographyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiographyHistory
        fields = ['abstract', 'content', 'sources', 'copyright']
        depth = 10


class LanguageScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageScript
        fields = ['language', 'script']
        depth = 10


class LocalDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalDescription
        fields = ['gender', 'notes', 'citation']
        depth = 10


class PlaceSerializer(serializers.ModelSerializer):
    place = GeonamesPlaceSerializer(many=False, read_only=True)

    class Meta:
        model = Place
        fields = ['place', 'address', 'role']
        depth = 10


class DescriptionSerializer(serializers.ModelSerializer):
    biography_history = BiographyHistorySerializer(read_only=True)
    languages_scripts = LanguageScriptSerializer(many=True, read_only=True)
    local_descriptions = LocalDescriptionSerializer(many=True, read_only=True)
    places = PlaceSerializer(many=True, read_only=True)

    class Meta:
        model = Description
        fields = ['biography_history', 'function', 'local_descriptions',
                  'languages_scripts', 'places', 'structure_or_genealogy']
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
    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        # TODO - check if fields are empty before adding them

        metadata = []

        # Entity Type
        if hasattr(obj, 'entity_type'):
            metadata.append({
                "name": "Entity Type",
                "content": obj.entity_type.title,
            })

        identities_list = obj.identities.order_by(
            '-preferred_identity')

        # Identities
        if identities_list.count():
            identities_json = []
            for identity in identities_list:
                identity_json = []

                preferred_name = identity.authorised_form
                other_names = identity.name_entries.exclude(
                    authorised_form=True)

                # Preferred Names
                if preferred_name:
                    identity_json.append({
                        "name": "Preferred Name",
                        "content": [
                            {
                                "name": "Name",
                                "content": "{} ({})".format(
                                    preferred_name.display_name,
                                    date_format(preferred_name.date_from,
                                                preferred_name.date_to)
                                )
                            },
                            {
                                "name": "Language",
                                "content": "{}, {}".format(
                                    preferred_name.language,
                                    preferred_name.script)
                            }
                        ]
                    })

                # Gender
                if identity.descriptions.count():
                    genders_json = []
                    for description in identity.descriptions.all():

                        local_descs = description.local_descriptions
                        if local_descs.count():
                            for local_desc in local_descs.all():
                                genders_json.append([{
                                    "name": "Gender",
                                    "content": "{} ({})".format(
                                        local_desc.gender,
                                        date_format(local_desc.date_from,
                                                    local_desc.date_to)

                                    )
                                }, {
                                    "name": "Notes",
                                    "content": local_desc.notes
                                }, {
                                    "name": "Citation",
                                    "content": local_desc.citation
                                }])
                    identity_json.append({
                        "name": "Genders",
                        "content": genders_json
                    })

                # Exist Dates
                identity_json.append({
                    "name": "Dates of Existence",
                    "content": date_format(
                        identity.date_from,
                        identity.date_to,
                    )
                })

                # Other Names
                if other_names.count():
                    other_names_json = []
                    for name in other_names.all():
                        other_names_json.append({
                            "name": "Name",
                            "content": "{} ({})".format(
                                name.display_name,
                                date_format(name.date_from,
                                            name.date_to)
                            )
                        })

                    identity_json.append({
                        "name": "Other Names",
                        "content": other_names_json
                    })

                # Bio/History
                if identity.descriptions.count():
                    bios_json = []

                    for description in identity.descriptions.all():
                        bio = description.biography_history
                        if bio:
                            bios_json.append([{
                                "name": "Abstract",
                                "content": bio.abstract
                            }, {
                                "name": "Content",
                                "content": bio.content
                            }, {
                                "name": "Sources",
                                "content": bio.sources
                            }, {
                                "name": "Copyright",
                                "content": bio.copyright
                            }])

                    identity_json.append({
                        "name": "Biography/History",
                        "content": bios_json
                    })

                # Relationships
                if identity.relations.count():
                    relations_json = []
                    for relation in identity.relations.all():
                        relations_json.append([{
                            "name": "Type",
                            "content": relation.relation_type.title
                        }, {
                            "name": "Related Entity",
                            "content": relation.related_entity.display_name
                        }, {
                            "name": "Notes",
                            "content": relation.notes
                        }, {
                            "name": "Dates",
                            "content": date_format(relation.date_from,
                                                   relation.date_to)
                        }, {
                            "name": "Place",
                            "content": str(relation.place)
                        }])

                    identity_json.append({
                        "name": "Relationships",
                        "content": relations_json
                    })

                # Genealogy
                if identity.descriptions.count():
                    genealogies_json = []
                    for description in identity.descriptions.all():
                        genealogies_json.append({
                            "name": "Genealogy",
                            "content": description.structure_or_genealogy
                        })
                    identity_json.append({
                        "name": "Genealogies",
                        "content": genealogies_json
                    })

                # LangScript
                if identity.descriptions.count():
                    langscripts_json = []
                    for description in identity.descriptions.all():

                        languages_scripts = description.languages_scripts
                        if languages_scripts.count():
                            for lang in languages_scripts.all():
                                langscripts_json.append([{
                                    "name": "Language",
                                    "content": str(lang.language)
                                }, {
                                    "name": "Script",
                                    "content": str(lang.script)
                                }])
                    identity_json.append({
                        "name": "Languages/Scripts",
                        "content": langscripts_json
                    })

                # Places
                if identity.descriptions.count():
                    places_json = []
                    for description in identity.descriptions.all():

                        places = description.places
                        if places.count():
                            for place in places.all():
                                places_json.append([{
                                    "name": "Place",
                                    "content": str(place.place)
                                }, {
                                    "name": "Address",
                                    "content": place.address
                                }, {
                                    "name": "Role",
                                    "content": place.role
                                }, {
                                    "name": "Dates",
                                    "content": date_format(place.date_from,
                                                           place.date_to)
                                }])
                    identity_json.append({
                        "name": "Places",
                        "content": places_json
                    })

                # Events TODO - check with Sam

                # Legal Statuses
                if identity.descriptions.count():
                    legal_statuses_json = []
                    for description in identity.descriptions.all():

                        legal_statuses = description.legal_statuses
                        if legal_statuses.count():
                            for status in legal_statuses.all():
                                legal_statuses_json.append([{
                                    "name": "Term",
                                    "content": status.term
                                }, {
                                    "name": "Citation",
                                    "content": status.citation
                                }, {
                                    "name": "Notes",
                                    "content": status.notes
                                }, {
                                    "name": "Dates",
                                    "content": date_format(status.date_from,
                                                           status.date_to)
                                }])
                    identity_json.append({
                        "name": "Legal Statuses",
                        "content": legal_statuses_json
                    })

                # Mandates
                if identity.descriptions.count():
                    mandates_json = []
                    for description in identity.descriptions.all():

                        mandates = description.mandates
                        if mandates.count():
                            for mandate in mandates.all():
                                mandates_json.append([{
                                    "name": "Term",
                                    "content": mandate.term
                                }, {
                                    "name": "Citation",
                                    "content": mandate.citation
                                }, {
                                    "name": "Notes",
                                    "content": mandate.notes
                                }, {
                                    "name": "Dates",
                                    "content": date_format(mandate.date_from,
                                                           mandate.date_to)
                                }])
                    identity_json.append({
                        "name": "Mandates",
                        "content": mandates_json
                    })

                # Resources
                if identity.resources.count():
                    resources_json = []
                    for resource in identity.resources.all():
                        resources_json.append([{
                            "name": "Type",
                            "content": resource.relation_type.title
                        }, {
                            "name": "URL",
                            "content": resource.url
                        }, {
                            "name": "Citation",
                            "content": resource.citation
                        }, {
                            "name": "Notes",
                            "content": resource.notes
                        }])

                    identity_json.append({
                        "name": "Resources",
                        "content": resources_json
                    })

                identities_json.append(identity_json)

        metadata.append({
            "name": "Identities",
            "content": identities_json,
        })

        # Admin - TODO (check with Sam)

        # And return...
        return metadata

    class Meta:
        model = Entity
        fields = ['id', 'url', 'display_name', 'entity_type',
                  'identities', 'descriptions', 'control', 'metadata']
        depth = 10
