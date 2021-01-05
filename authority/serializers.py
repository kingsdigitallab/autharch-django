from jargon.serializers import (
    EntityRelationTypeSerializer, EntityTypeSerializer,
    MaintenanceStatusSerializer, PublicationStatusSerializer,
    ResourceRelationTypeSerializer)
from rest_framework import serializers

from .models import (
    BiographyHistory, Control, Description, Entity, Function, Event, Identity,
    LegalStatus, LocalDescription, Mandate, NameEntry, Place, Relation,
    Resource, Source
)


class BiographyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BiographyHistory
        fields = ['abstract', 'content', 'sources', 'copyright']
        depth = 10


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['name', 'url', 'notes']
        depth = 10


class ControlSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()
    maintenance_status = MaintenanceStatusSerializer(read_only=True)
    publication_status = PublicationStatusSerializer(read_only=True)
    script = serializers.SerializerMethodField()
    sources = SourceSerializer(many=True, read_only=True)

    def get_language(self, obj):
        return obj.language.label

    def get_script(self, obj):
        return obj.script.name

    class Meta:
        model = Control
        fields = ['language', 'maintenance_status', 'publication_status',
                  'rights_declaration', 'rights_declaration_abbreviation',
                  'rights_declaration_citation', 'script', 'sources']


class EventSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    def get_place(self, obj):
        try:
            return obj.place.address
        except AttributeError:
            return ''

    class Meta:
        model = Event
        fields = ['event', 'place', 'display_date']
        depth = 10


class FunctionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.title.title

    class Meta:
        model = Function
        fields = ['title', 'display_date']
        depth = 10


class LegalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalStatus
        fields = ['term', 'notes', 'citation', 'display_date']
        depth = 10


class LocalDescriptionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.gender.title

    class Meta:
        model = LocalDescription
        fields = ['title', 'notes', 'citation', 'display_date']
        depth = 10


class MandateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandate
        fields = ['term', 'notes', 'citation', 'display_date']


class PlaceSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    def get_place(self, obj):
        try:
            return obj.place.address
        except AttributeError:
            return obj.address

    class Meta:
        model = Place
        fields = ['place', 'address', 'role', 'display_date']
        depth = 10


class DescriptionSerializer(serializers.ModelSerializer):
    biography_history = BiographyHistorySerializer(read_only=True)
    functions = FunctionSerializer(many=True, read_only=True)
    languages_scripts = serializers.SerializerMethodField()
    legal_statuses = LegalStatusSerializer(many=True, read_only=True)
    genders = LocalDescriptionSerializer(many=True, read_only=True,
                                         source='local_descriptions')
    events = EventSerializer(many=True, read_only=True)
    mandates = MandateSerializer(many=True, read_only=True)
    places = PlaceSerializer(many=True, read_only=True)

    def get_languages_scripts(self, obj):
        return [ls.language.label for ls in obj.languages_scripts.all()]

    class Meta:
        model = Description
        fields = ['biography_history', 'functions', 'genders', 'events',
                  'languages_scripts', 'legal_statuses', 'mandates', 'places']
        depth = 10


class NameEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NameEntry
        fields = ['display_name', 'authorised_form', 'date_from', 'date_to',
                  'display_date']


class RelatedEntitySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.display_name

    class Meta:
        model = Entity
        fields = ['id', 'name']


class RelationSerializer(serializers.ModelSerializer):
    related_entity = RelatedEntitySerializer(read_only=True)
    relation_type = EntityRelationTypeSerializer(read_only=True)

    class Meta:
        model = Relation
        fields = ['related_entity', 'relation_type', 'relation_detail',
                  'place']


class ResourceSerializer(serializers.ModelSerializer):
    relation_type = ResourceRelationTypeSerializer(read_only=True)

    class Meta:
        model = Resource
        fields = ['relation_type', 'url', 'citation', 'notes']


class IdentitySerializer(serializers.ModelSerializer):
    name_entries = NameEntrySerializer(many=True, read_only=True)
    descriptions = DescriptionSerializer(many=True, read_only=True)
    authorised_display_name = serializers.SerializerMethodField()
    related_entities = RelationSerializer(many=True, read_only=True,
                                          source='relations')
    resources = ResourceSerializer(many=True, read_only=True)

    def get_authorised_display_name(self, obj):
        try:
            name = obj.name_entries.filter(authorised_form=True)[0]
        except IndexError:
            name = obj.name_entries.all()[0]
        return name.display_name

    class Meta:
        model = Identity
        fields = ['preferred_identity', 'authorised_display_name',
                  'display_date', 'name_entries', 'descriptions',
                  'related_entities', 'resources']
        depth = 10


class EntitySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='entity-detail', lookup_field='pk'
    )

    entity_type = EntityTypeSerializer(many=False, read_only=True)
    identities = IdentitySerializer(many=True, read_only=True)
    control = ControlSerializer(many=False, read_only=True)
    # metadata = serializers.SerializerMethodField()

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
                                    preferred_name.get_date()
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
                                name.display_name, name.get_date()
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
                            "name": "Description",
                            "content": relation.relation_detail
                        }, {
                            "name": "Dates",
                            "content": relation.get_date()
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
                                        local_desc.get_date()
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

                        except BiographyHistory.DoesNotExist:
                            pass

                        # Events (OL - events were under bio/hist)
                        events = description.events
                        if events.count():
                            for e in events.all():
                                events_json.append([{
                                    "name": "Event",
                                    "content": e.event
                                }, {
                                    "name": "Place",
                                    "content": str(e.place)
                                }, {
                                    "name": "Dates",
                                    "content": e.get_date()
                                }])

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
                                    "content": place.get_date()
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
                                    "content": status.get_date()
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
                                    "content": mandate.get_date()
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
                    "content": identity.get_date()
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
                  'identities', 'control']  # , 'metadata']
        depth = 10
