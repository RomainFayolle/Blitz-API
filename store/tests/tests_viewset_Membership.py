import json

from datetime import timedelta

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from blitz_api.factories import UserFactory, AdminFactory
from blitz_api.models import AcademicLevel
from blitz_api.services import remove_translation_fields

from ..models import Membership

User = get_user_model()


class MembershipTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(MembershipTests, cls).setUpClass()
        cls.client = APIClient()
        cls.user = UserFactory()
        cls.admin = AdminFactory()
        cls.academic_level = AcademicLevel.objects.create(
            name="University"
        )
        cls.membership = Membership.objects.create(
            name="basic_membership",
            details="1-Year student membership",
            price=50,
            available=True,
            duration=timedelta(days=365),
        )
        cls.membership.academic_levels.set([cls.academic_level])
        cls.membership_unavailable = Membership.objects.create(
            name="pending_membership",
            details="todo",
            price=50,
            available=False,
            duration=timedelta(days=365),
        )
        cls.membership_unavailable.academic_levels.set([cls.academic_level])

    def test_create(self):
        """
        Ensure we can create a membership if user has permission.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "advanced_membership",
            'details': "3-Year student membership",
            'available': True,
            'price': 125,
            'duration': timedelta(days=365*3),
            'academic_levels': [reverse(
                'academiclevel-detail', args=[self.academic_level.id]
            )],
        }

        response = self.client.post(
            reverse('membership-list'),
            data,
            format='json',
        )

        response_data = remove_translation_fields(json.loads(response.content))
        del response_data['url']
        del response_data['id']

        content = {
            'available': True,
            'details': '3-Year student membership',
            'duration': '1095 00:00:00',
            'name': 'advanced_membership',
            'price': '125.00',
            'academic_levels': ['http://testserver/academic_levels/' +
                                str(self.academic_level.id)],
            'available_on_product_types': [],
            'available_on_products': [],
            'options': [],
            'picture': None,
        }

        self.assertEqual(
            response_data,
            content
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_without_permission(self):
        """
        Ensure we can't create a membership if user has no permission.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': "advanced_membership",
            'details': "3-Year student membership",
            'price': 125,
            'duration': timedelta(days=365*3),
            'academic_levels': [reverse(
                'academiclevel-detail', args=[self.academic_level.id]
            )],
        }

        response = self.client.post(
            reverse('membership-list'),
            data,
            format='json',
        )

        content = {
            'detail': 'You do not have permission to perform this action.'
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_missing_field(self):
        """
        Ensure we can't create a membership when required field are missing.
        """
        self.client.force_authenticate(user=self.admin)

        data = {}

        response = self.client.post(
            reverse('membership-list'),
            data,
            format='json',
        )

        content = {
            'duration': ['This field is required.'],
            'price': ['This field is required.'],
            'available': ['This field is required.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_null_field(self):
        """
        Ensure we can't create a membership when required field are null.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': None,
            'details': None,
            'price': None,
            'duration': None,
            'available': None,
        }

        response = self.client.post(
            reverse('membership-list'),
            data,
            format='json',
        )

        content = {
            'duration': ['This field may not be null.'],
            'name': ['This field may not be null.'],
            'price': ['This field may not be null.'],
            'available': ['This field may not be null.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_field(self):
        """
        Ensure we can't create a membership when required field are invalid.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "",
            'details': "",
            'price': "",
            'duration': "invalid",
            'academic_levels': "invalid",
            'available': "invalid",
        }

        response = self.client.post(
            reverse('membership-list'),
            data,
            format='json',
        )

        content = {
            'academic_levels': [
                'Expected a list of items but got type "str".'
            ],
            'duration': [
                'Duration has wrong format. Use one of these formats instead: '
                '[DD] [HH:[MM:]]ss[.uuuuuu].'
            ],
            'name': ['This field may not be blank.'],
            'price': ['A valid number is required.'],
            'available': ['Must be a valid boolean.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """
        Ensure we can update a membership.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "basic_membership_updated",
            'details': "1-Year student membership",
            'price': 10,
            'duration': timedelta(days=365),
            'available': True,
            # ManytoMany relationship not required for some reasons.
            # Needs investigtion.
            # 'academic_levels': [reverse(
            #     'academiclevel-detail', args=[self.academic_level.id]
            # )],
        }

        response = self.client.put(
            reverse(
                'membership-detail',
                kwargs={'pk': self.membership.id},
            ),
            data,
            format='json',
        )

        content = {
            'available': True,
            'details': '1-Year student membership',
            'duration': '365 00:00:00',
            'name': 'basic_membership_updated',
            'price': '10.00',
            'url': 'http://testserver/memberships/' + str(self.membership.id),
            'id': self.membership.id,
            'academic_levels': ['http://testserver/academic_levels/' +
                                str(self.academic_level.id)],
            'available_on_product_types': [],
            'available_on_products': [],
            'options': [],
            'picture': None,
        }

        self.assertEqual(
            remove_translation_fields(json.loads(response.content)),
            content
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_as_admin(self):
        """
        Ensure we can make a membership unavailable as an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'membership-detail',
                kwargs={'pk': self.membership.id},
            ),
        )
        membership = self.membership
        membership.refresh_from_db()

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(self.membership.available)

    def test_delete_as_user(self):
        """
        Ensure that a user can't make a membership unavailable.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'membership-detail',
                kwargs={'pk': self.membership.id},
            ),
        )

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_delete_inexistent(self):
        """
        Ensure that deleting a non-existent membership does nothing.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'membership-detail',
                kwargs={'pk': 999},
            ),
        )

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )

    def test_list(self):
        """
        Ensure we can list available memberships as an unauthenticated user.
        """
        response = self.client.get(
            reverse('membership-list'),
            format='json',
        )

        data = json.loads(response.content)

        content = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'available': True,
                'details': '1-Year student membership',
                'duration': '365 00:00:00',
                'name': 'basic_membership',
                'price': '50.00',
                'url': 'http://testserver/memberships/' +
                       str(self.membership.id),
                'id': self.membership.id,
                'academic_levels': ['http://testserver/academic_levels/' +
                                    str(self.academic_level.id)],
                'available_on_product_types': [],
                'available_on_products': [],
                'options': [],
                'picture': None,
            }]
        }

        self.assertEqual(data, content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_as_admin(self):
        """
        Ensure we can list all memberships as an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('membership-list'),
            format='json',
        )

        data = remove_translation_fields(json.loads(response.content))
        data['results'] = [
            remove_translation_fields(m) for m in data['results']
        ]

        content = {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'available': True,
                'id': self.membership.id,
                'details': '1-Year student membership',
                'duration': '365 00:00:00',
                'name': 'basic_membership',
                'price': '50.00',
                'url': 'http://testserver/memberships/' +
                       str(self.membership.id),
                'academic_levels': ['http://testserver/academic_levels/' +
                                    str(self.academic_level.id)],
                'available_on_product_types': [],
                'available_on_products': [],
                'options': [],
                'picture': None,
            }, {
                'available': False,
                'id': self.membership_unavailable.id,
                'details': 'todo',
                'duration': '365 00:00:00',
                'name': 'pending_membership',
                'price': '50.00',
                'url': 'http://testserver/memberships/' +
                       str(self.membership_unavailable.id),
                'academic_levels': ['http://testserver/academic_levels/' +
                                    str(self.academic_level.id)],
                'available_on_product_types': [],
                'available_on_products': [],
                'options': [],
                'picture': None,
            }]
        }

        self.assertEqual(data, content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read(self):
        """
        Ensure we can read a membership as an unauthenticated user.
        """

        response = self.client.get(
            reverse(
                'membership-detail',
                kwargs={'pk': self.membership.id},
            ),
        )

        content = {
            'available': True,
            'id': self.membership.id,
            'details': '1-Year student membership',
            'duration': '365 00:00:00',
            'name': 'basic_membership',
            'price': '50.00',
            'url': 'http://testserver/memberships/' + str(self.membership.id),
            'academic_levels': ['http://testserver/academic_levels/' +
                                str(self.academic_level.id)],
            'available_on_product_types': [],
            'available_on_products': [],
            'options': [],
            'picture': None,
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_as_admin(self):
        """
        Ensure we can read a membership as an unauthenticated user.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse(
                'membership-detail',
                kwargs={'pk': self.membership.id},
            ),
        )

        content = {
            'available': True,
            'id': self.membership.id,
            'details': '1-Year student membership',
            'duration': '365 00:00:00',
            'name': 'basic_membership',
            'price': '50.00',
            'url': 'http://testserver/memberships/' + str(self.membership.id),
            'academic_levels': ['http://testserver/academic_levels/' +
                                str(self.academic_level.id)],
            'available_on_product_types': [],
            'available_on_products': [],
            'options': [],
            'picture': None,
        }

        self.assertEqual(
            remove_translation_fields(json.loads(response.content)),
            content
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_non_existent(self):
        """
        Ensure we get not found when asking for a membership that doesn't
        exist.
        """

        response = self.client.get(
            reverse(
                'membership-detail',
                kwargs={'pk': 999},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
