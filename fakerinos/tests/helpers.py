from rest_framework.reverse import reverse
from mixer.backend.django import mixer


class ModelViewSetHelpersMixin:
    detail_endpoint = None
    list_endpoint = None
    model = None
    serializer_class = None
    lookup_field = 'pk'

    def get_detail_endpoint(self, lookup):
        assert self.detail_endpoint is not None
        return reverse(self.detail_endpoint, kwargs={self.lookup_field: lookup})

    def get_list_endpoint(self):
        assert self.list_endpoint is not None
        return reverse(self.list_endpoint)

    def list(self, expected_status, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.get(self.get_list_endpoint())
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))

    def retrieve(self, expected_status, lookup, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.get(self.get_detail_endpoint(lookup))
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))

    def create(self, expected_status, user=None):
        assert self.model is not None
        assert self.serializer_class is not None
        if user:
            self.client.force_login(user)
        instance = mixer.blend(self.model)
        response = self.client.post(self.get_list_endpoint(), data=self.serializer_class(instance).data)
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))

    def update(self, expected_status, lookup, data=None, user=None):
        if user:
            self.client.force_login(user)
        data = data or self.serializer_class(mixer.blend(self.model)).data
        response = self.client.put(self.get_detail_endpoint(lookup), data=data)
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))

    def partial_update(self, expected_status, lookup, data=None, user=None):
        if user:
            self.client.force_login(user)
        data = data or {}
        response = self.client.patch(self.get_detail_endpoint(lookup), data=data)
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))

    def delete(self, expected_status, lookup, user=None):
        if user:
            self.client.force_login(user)
        response = self.client.delete(self.get_detail_endpoint(lookup))
        if isinstance(expected_status, int):
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertTrue(expected_status(response.status_code))
