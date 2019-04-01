from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.contrib.auth.models import Permission, Group, User as Buser
from django.conf import settings
from mixer.backend.django import mixer
from .. import receivers

User = get_user_model()


class TestSignals(TestCase):
    def setUp(self):
        self.model = User

    def test_post_save_signal_sent(self):
        with patch.object(signals.post_save, 'send') as mock_signal:
            user = self.model.objects.create()
            self.assertEqual(mock_signal.call_count, 1)
            kwargs = mock_signal.call_args[1]
            self.assertEqual(kwargs['sender'], self.model)
            self.assertEqual(kwargs['instance'], user)
            self.assertEqual(kwargs['created'], True)

    def test_create_player_called(self):
        with patch.object(receivers, 'create_player') as mock_handler:
            signals.post_save.connect(mock_handler, sender=self.model)
            user = self.model.objects.create()
            self.assertEqual(mock_handler.call_count, 1)
            kwargs = mock_handler.call_args[1]
            self.assertEqual(kwargs['sender'], self.model)
            self.assertEqual(kwargs['instance'], user)
            self.assertEqual(kwargs['created'], True)

    def test_create_profile_called(self):
        with patch.object(receivers, 'create_profile') as mock_handler:
            signals.post_save.connect(mock_handler, sender=self.model)
            user = self.model.objects.create()
            self.assertEqual(mock_handler.call_count, 1)
            kwargs = mock_handler.call_args[1]
            self.assertEqual(kwargs['sender'], self.model)
            self.assertEqual(kwargs['instance'], user)
            self.assertEqual(kwargs['created'], True)

    def test_assign_default_user_group_called(self):
        with patch.object(receivers, 'assign_default_user_group') as mock_handler:
            signals.post_save.connect(mock_handler, sender=self.model)
            user = self.model.objects.create()
            self.assertEqual(mock_handler.call_count, 1)
            kwargs = mock_handler.call_args[1]
            self.assertEqual(kwargs['sender'], self.model)
            self.assertEqual(kwargs['instance'], user)
            self.assertEqual(kwargs['created'], True)

    def test_default_group_assigned(self):
        Group.objects.filter(name='default').delete()
        user = self.model.objects.create()
        self.assertTrue(Group.objects.filter(name='default').exists())
        self.assertTrue(user.groups.filter(name='default').exists())

    def test_assign_default_user_group_bad_perm_names(self):
        random_perm_names = [mixer.faker.pystr() for _ in range(100)]
        with patch.object(settings, 'DEFAULT_USER_PERMISSIONS', new=random_perm_names) as mock_perm_names:
            # self.assertRaises(ValueError, self.model.objects.create)
            user = self.model()
            self.assertRaises(ValueError, receivers.assign_default_user_group, self.model, user, True)

    def test_get_default_permissions_success(self):
        all_perms = Permission.objects.all()
        self.assertTrue(all_perms)
        all_perm_names = set(all_perms.values_list('codename', flat=True))
        self.assertEqual(len(all_perms), len(all_perm_names))
        default_perm_names = {perm.codename for perm in
                              receivers.get_default_permissions(permission_names=all_perm_names)}
        self.assertEqual(all_perm_names, default_perm_names)

    def test_get_default_permissions_bad_perm_names(self):
        random_perm_names = [mixer.faker.big_integer() for _ in range(10)]
        self.assertRaises(ValueError, receivers.get_default_permissions, permission_names=random_perm_names)
        random_perm_names = [mixer.faker.pystr() for _ in range(100)]
        self.assertRaises(ValueError, receivers.get_default_permissions, permission_names=random_perm_names)
