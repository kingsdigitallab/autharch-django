from django.test import TestCase
from authority.models import Entity


class TestEntity(TestCase):

    def setUp(self):
        pass

    def test_get_or_create_by_display_name(self):
        self.assertIsNone(Entity.get_or_create_by_display_name(
            None, None, None))

        name = 'Georgina, Queen'
        entity = Entity.get_or_create_by_display_name(name)
        self.assertIsNotNone(entity)
