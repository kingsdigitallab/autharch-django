from geonames_place.serializers import \
    PlaceSerializer as GeonamesPlaceSerializer
from jargon.serializers import EntityTypeSerializer
from rest_framework import serializers

from .models import (
    BiographyHistory, Control, Description, Entity, Identity, LanguageScript,
    LocalDescription, NameEntry, Place
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

                # Other Name
                other_names = identity.name_entries.exclude(
                    authorised_form=True)
                other_names_json = []
                if other_names.count():
                    for name in other_names.all():
                        other_names_json.append({
                            "name": "Name",
                            "content": "{} ({})".format(
                                name.display_name,
                                date_format(name.date_from,
                                            name.date_to)
                            )
                        })

                # Relationships
                relations_json = []
                if identity.relations.count():
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

                # Resources
                resources_json = []
                if identity.resources.count():
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

                # Admin
                admin_json = []

                # Record ID
                admin_json.append({
                    "name": "Record ID",
                    "content": obj.pk
                })

                try:
                    # Control date
                    control = obj.control
                    admin_json.append({
                        "name": "Language",
                        "content": str(control.language)
                    })
                    admin_json.append({
                        "name": "Script",
                        "content": str(control.script)
                    })
                    admin_json.append({
                        "name": "Maintenance Status",
                        "content": control.maintenance_status.title
                    })
                    admin_json.append({
                        "name": "Publication Status",
                        "content": control.publication_status.title
                    })
                    admin_json.append({
                        "name": "Rights Declaration",
                        "content": control.rights_declaration
                    })

                    # Sources
                    sources = control.sources
                    if sources.count():
                        sources_json = []
                        for source in sources.all():
                            sources_json.append([{
                                "name": "Name",
                                "content": source.name
                            }, {
                                "name": "URL",
                                "content": source.url
                            }, {
                                "name": "Notes",
                                "content": source.notes
                            }])
                        admin_json.append({
                            "name": "Sources",
                            "content": sources_json
                        })
                except Control.DoesNotExist:
                    pass

                # Descriptions
                genders_json = []
                bios_json = []
                events_json = []
                genealogies_json = []
                langscripts_json = []
                places_json = []
                legal_statuses_json = []
                functions_json = []
                mandates_json = []

                if identity.descriptions.count():
                    for description in identity.descriptions.all():

                        # Gender
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

                        try:
                            # Bio
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

                                # Events (under bio/hist)
                                for event in bio.events.all():
                                    events_json.append([{
                                        "name": "Event",
                                        "content": event.event
                                    }, {
                                        "name": "Place",
                                        "content": str(event.place)
                                    }, {
                                        "name": "Dates",
                                        "content": date_format(event.date_from,
                                                               event.date_to)
                                    }])
                        except BiographyHistory.DoesNotExist:
                            pass

                        # Genealogy
                        genealogies_json.append({
                            "name": "Genealogy",
                            "content": description.structure_or_genealogy
                        })

                        # Langscript
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

                        # Places
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

                        # Legal status
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

                        # functions
                        functions = description.function.all()
                        if functions.count():
                            for function in functions.all():
                                functions_json.append({
                                    "name": "Name",
                                    "content": function.title
                                })

                        # Mandates
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

                # Add stuff!
                if len(genders_json):
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
                if len(other_names_json):
                    identity_json.append({
                        "name": "Other Names",
                        "content": other_names_json
                    })

                # Bio/History
                if len(bios_json):
                    identity_json.append({
                        "name": "Biography/History",
                        "content": bios_json
                    })

                # Relations
                if len(relations_json):
                    identity_json.append({
                        "name": "Relationships",
                        "content": relations_json
                    })

                # Geneaologies
                if len(genealogies_json):
                    identity_json.append({
                        "name": "Genealogies",
                        "content": genealogies_json
                    })

                # Langscript
                if len(langscripts_json):
                    identity_json.append({
                        "name": "Languages/Scripts",
                        "content": langscripts_json
                    })

                # Places
                if len(places_json):
                    identity_json.append({
                        "name": "Places",
                        "content": places_json
                    })

                # Events
                if len(events_json):
                    identity_json.append({
                        "name": "Events",
                        "content": events_json
                    })

                # Legal status
                if len(legal_statuses_json):
                    identity_json.append({
                        "name": "Legal Statuses",
                        "content": legal_statuses_json
                    })

                # Functions
                if len(functions_json):
                    identity_json.append({
                        "name": "Functions",
                        "content": functions_json
                    })

                # Mandates
                if len(mandates_json):
                    identity_json.append({
                        "name": "Mandates",
                        "content": mandates_json
                    })

                # Resources
                if len(resources_json):
                    identity_json.append({
                        "name": "Resources",
                        "content": resources_json
                    })

                # Add the identity
                identities_json.append(identity_json)

        metadata.append({
            "name": "Identities",
            "content": identities_json,
        })

        metadata.append({
            "name": "Admin",
            "content": admin_json,
        })

        # Admin - TODO (check with Sam)

        # And return...
        return metadata

    class Meta:
        model = Entity
        fields = ['id', 'url', 'display_name', 'entity_type',
                  'identities', 'descriptions', 'control', 'metadata']
        depth = 10
