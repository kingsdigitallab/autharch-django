from django.test import TestCase

from authority.models import Entity, Identity
from editor.forms import EntityEditForm
from jargon.models import EntityType, NamePartType

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
