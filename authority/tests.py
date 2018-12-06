from authority.models import Entity, Identity, NameEntry
from django.test import TestCase
from django.utils import timezone
from jargon.models import EntityType
from languages_plus.models import Language
from script_codes.models import Script


class TestEntity(TestCase):

    def setUp(self):
        self.language, _ = Language.objects.get_or_create(
            iso_639_1='en', name_en='English', name_native='English',
            family='Indo-European')

        self.script, _ = Script.objects.get_or_create(
            code='Latn', number=215, name='Latin')

    def test_get_or_create_by_display_name(self):
        self.assertIsNone(Entity.get_or_create_by_display_name(
            None, None, None)[0])

        name = 'Georgina, Queen'

        entity, created = Entity.get_or_create_by_display_name(
            name, self.language, self.script)
        self.assertIsNotNone(entity)
        self.assertEquals(name, entity.display_name)
        self.assertTrue(created)

        entity, created = Entity.get_or_create_by_display_name(
            name, self.language, self.script)
        self.assertIsNotNone(entity)
        self.assertEquals(name, entity.display_name)
        self.assertFalse(created)

        et, _ = EntityType.objects.get_or_create(title='Person')

        entity = Entity(entity_type=et)
        entity.save()

        identity = Identity(entity=entity)
        identity.date_from = timezone.now()
        identity.preferred_identity = True
        identity.save()

        name_entry = NameEntry(identity=identity)
        name_entry.display_name = name
        name_entry.authorised_form = True
        name_entry.date_from = identity.date_from
        name_entry.language = self.language
        name_entry.script = self.script
        name_entry.save()

        entity, created = Entity.get_or_create_by_display_name(
            name, self.language, self.script)
        self.assertIsNone(entity)
        self.assertFalse(created)
