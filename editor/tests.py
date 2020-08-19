from django.test import TestCase

from geonames_place.models import Place as GeoPlace

from archival.models import File, Item, Project
from authority.exceptions import EntityMergeException
from authority.models import (
    BiographyHistory, Control, Description, Entity, Event, Function, Identity,
    LanguageScript, LegalStatus, LocalDescription, Mandate, NameEntry,
    NamePart, Place, Relation, Resource, Source)
from editor.forms import EntityEditForm
from jargon.models import (
    CollaborativeWorkspaceEditorType as CWEditorType, EditingEventType,
    EntityRelationType, EntityType, Function as JFunction, Gender,
    MaintenanceStatus, NamePartType, PublicationStatus, Repository,
    ResourceRelationType)

from controlled_vocabulary.utils import search_term_or_none
from script_codes.models import Script


class ContainerModelFormTestCase(TestCase):

    """These tests are currently very susceptible to changes in the minor
    configuration of formsets, such as the number of extra forms. This
    needs to be worked around in some fashion for these to be of much
    use."""

    @classmethod
    def setUpTestData(cls):
        cls.entity_type1 = EntityType(title='person')
        cls.entity_type1.save()
        cls.entity_type2 = EntityType(title='corporateBody')
        cls.entity_type2.save()
        cls.language1 = search_term_or_none('iso639-2', 'eng', exact=True)
        cls.script1 = Script.objects.all()[0]
        cls.name_part_type1 = NamePartType(title='Stage name')
        cls.name_part_type1.save()

    def test_delete_existing_with_new_related(self):
        """Tests deleting an existing inline formset's form with new related
        material."""
        self.assertEqual(Entity.objects.count(), 0)
        entity = Entity(entity_type=self.entity_type1)
        entity.save()
        identity = Identity(entity=entity, preferred_identity=True,
                            display_date='1912')
        identity.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        post_data = {
            'control-TOTAL_FORMS': 0,
            'control-INITIAL_FORMS': 0,
            'control-MIN_NUM_FORMS': 0,
            'control-MAX_NUM_FORMS': 1,
            'identity-TOTAL_FORMS': 1,
            'identity-INITIAL_FORMS': 1,
            'identity-MIN_NUM_FORMS': 0,
            'identity-MAX_NUM_FORMS': 1000,
            'identity-0-id': identity.pk,
            'identity-0-display_date': '1912',
            'identity-0-preferred_identity': 1,
            'identity-0-DELETE': 1,
            'identity-0-display_date': '1912',
            'identity-0-preferred_identity': 1,
            'identity-0-description-TOTAL_FORMS': 0,
            'identity-0-description-INITIAL_FORMS': 0,
            'identity-0-description-MIN_NUM_FORMS': 0,
            'identity-0-description-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-TOTAL_FORMS': 0,
            'identity-0-name_entry-INITIAL_FORMS': 0,
            'identity-0-name_entry-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-MAX_NUM_FORMS': 1000,
            'identity-0-relation-TOTAL_FORMS': 0,
            'identity-0-relation-INITIAL_FORMS': 0,
            'identity-0-relation-MIN_NUM_FORMS': 0,
            'identity-0-relation-MAX_NUM_FORMS': 0,
            'identity-0-resource-TOTAL_FORMS': 0,
            'identity-0-resource-INITIAL_FORMS': 0,
            'identity-0-resource-MIN_NUM_FORMS': 0,
            'identity-0-resource-MAX_NUM_FORMS': 0,
        }
        form = EntityEditForm(post_data, instance=entity)
        self.assertTrue(form.is_valid())
        entity = form.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 0)

    def test_delete_new_related(self):
        """Tests deleting an inline formset's form that hasn't been saved."""
        self.assertEqual(Entity.objects.count(), 0)
        entity = Entity(entity_type=self.entity_type1)
        entity.save()
        identity = Identity(entity=entity, preferred_identity=True,
                            display_date='1912')
        identity.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        post_data = {
            'control-TOTAL_FORMS': 0,
            'control-INITIAL_FORMS': 0,
            'control-MIN_NUM_FORMS': 0,
            'control-MAX_NUM_FORMS': 1,
            'identity-TOTAL_FORMS': 1,
            'identity-INITIAL_FORMS': 1,
            'identity-MIN_NUM_FORMS': 0,
            'identity-MAX_NUM_FORMS': 1000,
            'identity-0-id': identity.pk,
            'identity-0-display_date': '1912',
            'identity-0-preferred_identity': 1,
            'identity-0-description-TOTAL_FORMS': 0,
            'identity-0-description-INITIAL_FORMS': 0,
            'identity-0-description-MIN_NUM_FORMS': 0,
            'identity-0-description-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-TOTAL_FORMS': 1,
            'identity-0-name_entry-INITIAL_FORMS': 0,
            'identity-0-name_entry-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-0-display_name': 'Petra',
            'identity-0-name_entry-0-language': self.language1.pk,
            'identity-0-name_entry-0-script': self.script1.pk,
            'identity-0-name_entry-0-DELETE': 1,
            'identity-0-name_entry-0-name_part-TOTAL_FORMS': 0,
            'identity-0-name_entry-0-name_part-INITIAL_FORMS': 0,
            'identity-0-name_entry-0-name_part-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-0-name_part-MAX_NUM_FORMS': 0,
            'identity-0-relation-TOTAL_FORMS': 0,
            'identity-0-relation-INITIAL_FORMS': 0,
            'identity-0-relation-MIN_NUM_FORMS': 0,
            'identity-0-relation-MAX_NUM_FORMS': 0,
            'identity-0-resource-TOTAL_FORMS': 0,
            'identity-0-resource-INITIAL_FORMS': 0,
            'identity-0-resource-MIN_NUM_FORMS': 0,
            'identity-0-resource-MAX_NUM_FORMS': 0,
        }
        form = EntityEditForm(post_data, instance=entity)
        self.assertTrue(form.is_valid())
        entity = form.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.entity_type, self.entity_type1)
        self.assertEqual(entity.identities.count(), 1)
        self.assertEqual(entity.identities.all()[0].name_entries.count(), 0)

    def test_save_existing_root_new_related(self):
        """Tests saving changes to an existing Entity and adding related
        data."""
        self.assertEqual(Entity.objects.count(), 0)
        entity = Entity(entity_type=self.entity_type1)
        entity.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        post_data = {
            'control-TOTAL_FORMS': 0,
            'control-INITIAL_FORMS': 0,
            'control-MIN_NUM_FORMS': 0,
            'control-MAX_NUM_FORMS': 1,
            'identity-TOTAL_FORMS': 1,
            'identity-INITIAL_FORMS': 0,
            'identity-MIN_NUM_FORMS': 0,
            'identity-MAX_NUM_FORMS': 1000,
            'identity-0-display_date': '1912',
            'identity-0-description-TOTAL_FORMS': 0,
            'identity-0-description-INITIAL_FORMS': 0,
            'identity-0-description-MIN_NUM_FORMS': 0,
            'identity-0-description-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-TOTAL_FORMS': 0,
            'identity-0-name_entry-INITIAL_FORMS': 0,
            'identity-0-name_entry-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-MAX_NUM_FORMS': 1000,
            'identity-0-relation-TOTAL_FORMS': 0,
            'identity-0-relation-INITIAL_FORMS': 0,
            'identity-0-relation-MIN_NUM_FORMS': 0,
            'identity-0-relation-MAX_NUM_FORMS': 1000,
            'identity-0-resource-TOTAL_FORMS': 0,
            'identity-0-resource-INITIAL_FORMS': 0,
            'identity-0-resource-MIN_NUM_FORMS': 0,
            'identity-0-resource-MAX_NUM_FORMS': 1000,
        }
        form = EntityEditForm(post_data, instance=entity)
        self.assertTrue(form.is_valid())
        entity = form.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        self.assertEqual(entity.identities.all()[0].display_date, '1912')

    def test_save_existing_root_change_related(self):
        """Tests saving changes to an existing Entity and its related data."""
        self.assertEqual(Entity.objects.count(), 0)
        entity = Entity(entity_type=self.entity_type1)
        entity.save()
        identity = Identity(entity=entity, preferred_identity=True,
                            display_date='1912')
        identity.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        post_data = {
            'control-TOTAL_FORMS': 0,
            'control-INITIAL_FORMS': 0,
            'control-MIN_NUM_FORMS': 0,
            'control-MAX_NUM_FORMS': 1,
            'identity-TOTAL_FORMS': 1,
            'identity-INITIAL_FORMS': 1,
            'identity-MIN_NUM_FORMS': 0,
            'identity-MAX_NUM_FORMS': 1000,
            'identity-0-id': identity.pk,
            'identity-0-display_date': '1812',
            'identity-0-preferred_identity': 1,
            'identity-0-description-TOTAL_FORMS': 0,
            'identity-0-description-INITIAL_FORMS': 0,
            'identity-0-description-MIN_NUM_FORMS': 0,
            'identity-0-description-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-TOTAL_FORMS': 0,
            'identity-0-name_entry-INITIAL_FORMS': 0,
            'identity-0-name_entry-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-MAX_NUM_FORMS': 1000,
            'identity-0-relation-TOTAL_FORMS': 0,
            'identity-0-relation-INITIAL_FORMS': 0,
            'identity-0-relation-MIN_NUM_FORMS': 0,
            'identity-0-relation-MAX_NUM_FORMS': 1000,
            'identity-0-resource-TOTAL_FORMS': 0,
            'identity-0-resource-INITIAL_FORMS': 0,
            'identity-0-resource-MIN_NUM_FORMS': 0,
            'identity-0-resource-MAX_NUM_FORMS': 1000,
        }
        form = EntityEditForm(post_data, instance=entity)
        self.assertTrue(form.is_valid())
        entity = form.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        self.assertEqual(entity.identities.all()[0].display_date, '1812')

    def test_save_existing_root_new_related_two_levels(self):
        """Tests saving an existing Entity and new related data at two levels'
        remove."""
        self.assertEqual(Entity.objects.count(), 0)
        entity = Entity(entity_type=self.entity_type1)
        entity.save()
        identity = Identity(entity=entity, preferred_identity=True,
                            display_date='1912')
        identity.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        post_data = {
            'control-TOTAL_FORMS': 0,
            'control-INITIAL_FORMS': 0,
            'control-MIN_NUM_FORMS': 0,
            'control-MAX_NUM_FORMS': 1,
            'identity-TOTAL_FORMS': 1,
            'identity-INITIAL_FORMS': 1,
            'identity-MIN_NUM_FORMS': 0,
            'identity-MAX_NUM_FORMS': 1000,
            'identity-0-id': identity.pk,
            'identity-0-display_date': '1912',
            'identity-0-preferred_identity': 1,
            'identity-0-description-TOTAL_FORMS': 0,
            'identity-0-description-INITIAL_FORMS': 0,
            'identity-0-description-MIN_NUM_FORMS': 0,
            'identity-0-description-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-TOTAL_FORMS': 1,
            'identity-0-name_entry-INITIAL_FORMS': 0,
            'identity-0-name_entry-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-0-display_name': 'Petra',
            'identity-0-name_entry-0-language': self.language1.pk,
            'identity-0-name_entry-0-script': self.script1.pk,
            'identity-0-name_entry-0-name_part-TOTAL_FORMS': 1,
            'identity-0-name_entry-0-name_part-INITIAL_FORMS': 0,
            'identity-0-name_entry-0-name_part-MIN_NUM_FORMS': 0,
            'identity-0-name_entry-0-name_part-MAX_NUM_FORMS': 1000,
            'identity-0-name_entry-0-name_part-0-name_part_type':
            self.name_part_type1.pk,
            'identity-0-name_entry-0-name_part-0-part': 'the Rock',
            'identity-0-relation-TOTAL_FORMS': 0,
            'identity-0-relation-INITIAL_FORMS': 0,
            'identity-0-relation-MIN_NUM_FORMS': 0,
            'identity-0-relation-MAX_NUM_FORMS': 1000,
            'identity-0-resource-TOTAL_FORMS': 0,
            'identity-0-resource-INITIAL_FORMS': 0,
            'identity-0-resource-MIN_NUM_FORMS': 0,
            'identity-0-resource-MAX_NUM_FORMS': 1000,
        }
        form = EntityEditForm(post_data, instance=entity)
        self.assertTrue(form.is_valid())
        entity = form.save()
        self.assertEqual(Entity.objects.count(), 1)
        self.assertEqual(Entity.objects.all()[0], entity)
        self.assertEqual(entity.identities.count(), 1)
        self.assertEqual(entity.identities.all()[0].name_entries.count(), 1)


class MergeEntitiesTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.entity_type1 = EntityType(title='person')
        cls.entity_type1.save()
        cls.entity_type2 = EntityType(title='corporateBody')
        cls.entity_type2.save()
        cls.function1, _ = JFunction.objects.get_or_create(
            title='Policing practice')
        cls.gender1, _ = Gender.objects.get_or_create(title='Women')
        cls.language1 = search_term_or_none('iso639-2', 'eng', exact=True)
        cls.language2 = search_term_or_none('iso639-2', 'fra', exact=True)
        cls.script1 = Script.objects.all()[0]
        cls.name_part_type1 = NamePartType(title='Stage name')
        cls.name_part_type1.save()
        cls.project1 = Project(title='Project 1', slug='project1')
        cls.project1.save()
        cls.project2 = Project(title='Project 2', slug='project2')
        cls.project2.save()
        cls.ms, _ = MaintenanceStatus.objects.get_or_create(title='new')
        cls.ps, _ = PublicationStatus.objects.get_or_create(title='published')
        cls.erel_type1, _ = EntityRelationType.objects.get_or_create(
            title='temporal')
        cls.rrel_type1, _ = ResourceRelationType.objects.get_or_create(
            title='creatorOf')
        deleted_event_type = EditingEventType(title='deleted')
        deleted_event_type.save()
        revised_event_type = EditingEventType(title='revised')
        revised_event_type.save()
        human_editor_type = CWEditorType(title='human')
        human_editor_type.save()
        inprocess_publication_status = PublicationStatus(title='inProcess')
        inprocess_publication_status.save()
        deleted_maintenance_status = MaintenanceStatus(title='deleted')
        deleted_maintenance_status.save()
        cls.repository, _ = Repository.objects.get_or_create(
            title='Royal Archives', code=262)

    def _create_entity(self):
        entity = Entity(entity_type=self.entity_type1, project=self.project1)
        entity.save()
        identity = Identity(entity=entity, preferred_identity=True)
        identity.save()
        control = Control(entity=entity, maintenance_status=self.ms,
                          publication_status=self.ps, language=self.language1,
                          script=self.script1)
        control.save()
        return entity, identity, control

    def _create_record(self, record_model, uuid):
        record = record_model(
            uuid=uuid, project=self.project1, repository=self.repository,
            title='Test Record', start_date='2020',
            maintenance_status=self.ms, publication_status=self.ps,
            language=self.language1, script=self.script1)
        record.save()
        return record

    def test_merge_name(self):
        e1, e1_i1, e1_c = self._create_entity()
        e1_i1_ne1 = NameEntry(identity=e1_i1, display_name='Name 1',
                              authorised_form=True, language=self.language1,
                              script=self.script1)
        e1_i1_ne1.save()

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_ne1 = NameEntry(identity=e2_i1, display_name='Name 2',
                              authorised_form=True, language=self.language1,
                              script=self.script1)
        e2_i1_ne1.save()
        e2_i1_np1 = NamePart(name_entry=e2_i1_ne1, part='Name Part 1',
                             name_part_type=self.name_part_type1)
        e2_i1_np1.save()
        e2_i1_ne2 = NameEntry(identity=e2_i1, display_name='Name 1',
                              authorised_form=False, language=self.language1,
                              script=self.script1)
        e2_i1_ne2.save()

        e1.merge(e2)
        self.assertEqual(e1.identities.count(), 2)
        self.assertEqual(e2.identities.count(), 1)
        merged_i = e1.identities.get(preferred_identity=False)
        self.assertEqual(merged_i.name_entries.count(), 2)
        merged_ne = merged_i.name_entries.get(authorised_form=True)
        self.assertEqual(merged_ne.parts.count(), 1)
        self.assertEqual(merged_ne.parts.all()[0].part, 'Name Part 1')

    def test_merge_biography(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(BiographyHistory.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_b = BiographyHistory(description=e2_i1_d, abstract='Abstract')
        e2_i1_d_b.save()
        self.assertEqual(BiographyHistory.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(BiographyHistory.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(BiographyHistory.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(BiographyHistory.objects.filter(
            abstract='Abstract').count(), 2)

    def test_merge_event(self):
        e1, e1_i1, e1_c = self._create_entity()
        e1_i1_d = Description(identity=e1_i1)
        e1_i1_d.save()
        e1_i1_d_e1 = Event(description=e1_i1_d, event='Entity 1 Event')
        e1_i1_d_e1.save()
        self.assertEqual(Event.objects.filter(
            description__identity__entity=e1).count(), 1)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_e1 = Event(description=e2_i1_d, event='Entity 2 Event')
        e2_i1_d_e1.save()
        self.assertEqual(Event.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(Event.objects.filter(
            description__identity__entity=e1).count(), 2)
        self.assertEqual(Event.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(Event.objects.filter(event='Entity 2 Event').count(),
                         2)

    def test_merge_function(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Function.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_f1 = Function(description=e2_i1_d, title=self.function1)
        e2_i1_d_f1.save()
        self.assertEqual(Function.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(Function.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(Function.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(Function.objects.filter(
            title=self.function1).count(), 2)

    def test_merge_language_script(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(LanguageScript.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_l1 = LanguageScript(
            description=e2_i1_d, language=self.language1, script=self.script1)
        e2_i1_d_l1.save()
        self.assertEqual(LanguageScript.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(LanguageScript.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(LanguageScript.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(LanguageScript.objects.filter(
            language=self.language1).count(), 2)

    def test_merge_legal_status(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(LegalStatus.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_l1 = LegalStatus(description=e2_i1_d, term='Test')
        e2_i1_d_l1.save()
        self.assertEqual(LegalStatus.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(LegalStatus.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(LegalStatus.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(LegalStatus.objects.filter(term='Test').count(), 2)

    def test_merge_local_description(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(LocalDescription.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_l1 = LocalDescription(description=e2_i1_d, gender=self.gender1)
        e2_i1_d_l1.save()
        self.assertEqual(LocalDescription.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(LocalDescription.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(LocalDescription.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(LocalDescription.objects.filter(
            gender=self.gender1).count(), 2)

    def test_merge_mandate(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Mandate.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_l1 = Mandate(description=e2_i1_d, term='Test')
        e2_i1_d_l1.save()
        self.assertEqual(Mandate.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(Mandate.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(Mandate.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(Mandate.objects.filter(term='Test').count(), 2)

    def test_merge_place(self):
        place = GeoPlace.get_or_create_from_geonames('London')
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Place.objects.filter(
            description__identity__entity=e1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_d = Description(identity=e2_i1)
        e2_i1_d.save()
        e2_i1_d_l1 = Place(description=e2_i1_d, place=place)
        e2_i1_d_l1.save()
        self.assertEqual(Place.objects.filter(
            description__identity__entity=e2).count(), 1)

        e1.merge(e2)
        self.assertEqual(Place.objects.filter(
            description__identity__entity=e1).count(), 1)
        self.assertEqual(Place.objects.filter(
            description__identity__entity=e2).count(), 1)
        self.assertEqual(Place.objects.filter(place=place).count(), 2)

    def test_merge_relation(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Relation.objects.filter(identity=e1_i1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(Relation.objects.filter(identity=e2_i1).count(), 0)

        e3, e3_i1, e3_c = self._create_entity()
        e3_i1_r1 = Relation(identity=e3_i1, relation_type=self.erel_type1,
                            related_entity=e2, relation_detail='Test')
        e3_i1_r1.save()
        self.assertEqual(Relation.objects.filter(identity=e3_i1).count(), 1)

        e1.merge(e3)
        self.assertEqual(Relation.objects.filter(identity__entity=e1).count(),
                         1)
        self.assertEqual(Relation.objects.filter(identity__entity=e2).count(),
                         0)
        self.assertEqual(Relation.objects.filter(identity__entity=e3).count(),
                         1)
        self.assertEqual(Relation.objects.filter(
            relation_detail='Test').count(), 2)

    def test_merge_resource(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Resource.objects.filter(identity=e1_i1).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_i1_r1 = Resource(
            identity=e2_i1, relation_type=self.rrel_type1,
            url='http://example.org/', citation='Test')
        e2_i1_r1.save()
        self.assertEqual(Resource.objects.filter(identity=e2_i1).count(), 1)

        e1.merge(e2)
        self.assertEqual(Resource.objects.filter(
            identity__entity=e1).count(), 1)
        self.assertEqual(Resource.objects.filter(
            identity__entity=e2).count(), 1)
        self.assertEqual(Resource.objects.filter(
            citation='Test').count(), 2)

    def test_merge_source(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(Source.objects.filter(control=e1_c).count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        e2_c_s1 = Source(control=e2_c, name='Entity 2 Source 1')
        e2_c_s1.save()

        e1.merge(e2)
        self.assertEqual(Source.objects.filter(control=e1_c).count(), 1)
        self.assertEqual(Source.objects.get(control=e1_c).name,
                         'Entity 2 Source 1')

    def test_merge_person_subject_for_records(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.person_subject_for_records.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.person_subject_for_records.count(), 0)

        f = self._create_record(File, '1')
        f.persons_as_subjects.add(e2)
        self.assertEqual(e2.person_subject_for_records.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.person_subject_for_records.count(), 1)
        self.assertEqual(e2.person_subject_for_records.count(), 1)

    def test_merge_related_entities(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.related_entities.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.related_entities.count(), 0)

        f = self._create_record(File, '1')
        f.related_entities.add(e2)
        self.assertEqual(e2.related_entities.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.related_entities.count(), 1)
        self.assertEqual(e2.related_entities.count(), 1)

    def test_merge_organisation_subject_for_records(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.organisation_subject_for_records.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.organisation_subject_for_records.count(), 0)

        f = self._create_record(File, '1')
        f.organisations_as_subjects.add(e2)
        self.assertEqual(e2.organisation_subject_for_records.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.organisation_subject_for_records.count(), 1)
        self.assertEqual(e2.organisation_subject_for_records.count(), 1)

    def test_merge_files_created(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.files_created.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.files_created.count(), 0)

        f = self._create_record(File, '1')
        f.creators.add(e2)
        self.assertEqual(e2.files_created.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.files_created.count(), 1)
        self.assertEqual(e2.files_created.count(), 1)

    def test_merge_items_created(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.items_created.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.items_created.count(), 0)

        item = self._create_record(Item, '1')
        item.creators.add(e2)
        self.assertEqual(e2.items_created.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.items_created.count(), 1)
        self.assertEqual(e2.items_created.count(), 1)

    def test_merge_files_as_relations(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.files_as_relations.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.files_as_relations.count(), 0)

        f = self._create_record(File, '1')
        f.persons_as_relations.add(e2)
        self.assertEqual(e2.files_as_relations.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.files_as_relations.count(), 1)
        self.assertEqual(e2.files_as_relations.count(), 1)

    def test_merge_items_as_relations(self):
        e1, e1_i1, e1_c = self._create_entity()
        self.assertEqual(e1.items_as_relations.count(), 0)

        e2, e2_i1, e2_c = self._create_entity()
        self.assertEqual(e2.items_as_relations.count(), 0)

        item = self._create_record(Item, '1')
        item.persons_as_relations.add(e2)
        self.assertEqual(e2.items_as_relations.count(), 1)

        e1.merge(e2)
        self.assertEqual(e1.items_as_relations.count(), 1)
        self.assertEqual(e2.items_as_relations.count(), 1)

    def test_merge_other_deleted(self):
        e1, e1_i1, e1_c = self._create_entity()
        e2, e2_i1, e2_c = self._create_entity()

        e1.merge(e2)
        self.assertTrue(e2.is_deleted())

    def test_merge_different_entity_types(self):
        e1 = Entity(entity_type=self.entity_type1, project=self.project1)
        e1.save()
        e2 = Entity(entity_type=self.entity_type2, project=self.project1)
        e2.save()
        self.assertRaises(EntityMergeException, e1.merge, e2)

    def test_merge_different_projects(self):
        e1 = Entity(entity_type=self.entity_type1, project=self.project1)
        e1.save()
        e2 = Entity(entity_type=self.entity_type1, project=self.project2)
        e2.save()
        self.assertRaises(EntityMergeException, e1.merge, e2)
        e2.project = None
        e2.save()
        self.assertRaises(EntityMergeException, e2.merge, e1)

    def test_merge_non_entity(self):
        e1 = Entity(entity_type=self.entity_type1, project=self.project1)
        e1.save()
        self.assertRaises(EntityMergeException, e1.merge, self.project1)

    def test_merge_same_entity(self):
        e1 = Entity(entity_type=self.entity_type1, project=self.project1)
        e1.save()
        self.assertRaises(EntityMergeException, e1.merge, e1)
