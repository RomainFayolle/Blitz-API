import json

from datetime import timedelta

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from blitz_api.factories import UserFactory, AdminFactory
from blitz_api.models import AcademicLevel

from ..models import Membership, Order, OrderLine, Package

User = get_user_model()


class OrderLineTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(OrderLineTests, cls).setUpClass()
        cls.client = APIClient()
        cls.user = UserFactory()
        cls.admin = AdminFactory()
        cls.package_type = ContentType.objects.get_for_model(Package)
        cls.academic_level = AcademicLevel.objects.create(
            name="University"
        )
        cls.membership_with_academic_level = Membership.objects.create(
            name="basic_membership",
            details="1-Year student membership",
            available=True,
            price=50,
            duration=timedelta(days=365),
        )
        cls.membership_with_academic_level.academic_levels.set([
            cls.academic_level
        ])
        cls.membership = Membership.objects.create(
            name="basic_membership",
            details="1-Year student membership",
            available=True,
            price=50,
            duration=timedelta(days=365),
        )
        cls.package = Package.objects.create(
            name="extreme_package",
            details="100 reservations package",
            available=True,
            price=40,
            reservations=100,
        )
        cls.package.exclusive_memberships.set([
            cls.membership,
        ])
        cls.order = Order.objects.create(
            user=cls.user,
            transaction_date=timezone.now(),
            authorization_id=1,
            settlement_id=1,
        )
        cls.order_admin = Order.objects.create(
            user=cls.admin,
            transaction_date=timezone.now(),
            authorization_id=1,
            settlement_id=1,
        )
        cls.order_line = OrderLine.objects.create(
            order=cls.order,
            quantity=1,
            content_type=cls.package_type,
            object_id=cls.package.id,
            cost=cls.package.price,
        )
        cls.order_line_admin = OrderLine.objects.create(
            order=cls.order_admin,
            quantity=99,
            content_type=cls.package_type,
            object_id=cls.package.id,
            cost=99 * cls.package.price,
        )

        cls.maxDiff = 5000

    def test_create_package(self):
        """
        Ensure we can create an order line if user has permission.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 2,
            'content_type': "package",
            'object_id': self.package.id,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
        )

        content = {
            'content_type': 'package',
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 2,
            'coupon': None,
            'coupon_real_value': 0.0,
            'cost': 2 * self.package.price,
            'metadata': None,
            'options': []
        }

        response_content = json.loads(response.content)

        del response_content['id']
        del response_content['url']

        self.assertEqual(response_content, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_without_academic_level(self):
        """
        Ensure we can't create an order line with a membership if the user does
        not have the required academic level.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 1,
            'content_type': "membership",
            'object_id': self.membership_with_academic_level.id,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        content = {
            'object_id': [
                'User does not have the required academic_level to order this '
                'membership.'
            ]
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inexistent_object(self):
        """
        Ensure we can't create an order line if the reference object does
        not exist.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 2,
            'content_type': "package",
            'object_id': 999,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        content = {
            'object_id': ['The referenced object does not exist.']
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_membership(self):
        """
        Ensure we can create an order line if user has the required membership.
        """
        self.user.membership = self.membership
        self.client.force_authenticate(user=self.user)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 2,
            'content_type': "package",
            'object_id': self.package.id,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        self.user.membership = None

        content = {
            'content_type': 'package',
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 2,
            'coupon': None,
            'coupon_real_value': 0,
            'cost': 2.0 * self.package.price,
            'metadata': None,
            'options': []
        }

        response_content = json.loads(response.content)
        del response_content['id']
        del response_content['url']

        self.assertEqual(response_content, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_membership(self):
        """
        Ensure we can create an order line if user has permission.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 1,
            'content_type': "membership",
            'object_id': self.membership.id,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
        )

        content = {
            'content_type': 'membership',
            'coupon': None,
            'coupon_real_value': 0.0,
            'object_id': self.membership.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 1,
            'cost': self.membership.price,
            'metadata': None,
            'options': []
        }

        response_content = json.loads(response.content)
        del response_content['id']
        del response_content['url']

        self.assertEqual(response_content, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_field(self):
        """
        Ensure we can't create an order line when required field are missing.
        """
        self.client.force_authenticate(user=self.admin)

        data = {}

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        content = {
            'content_type': ['This field is required.'],
            'object_id': ['This field is required.'],
            'order': ['This field is required.'],
            'quantity': ['This field is required.']
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_null_field(self):
        """
        Ensure we can't create an order line when required field are null.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'content_type': None,
            'object_id': None,
            'order': None,
            'quantity': None,
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        content = {
            'content_type': ['This field may not be null.'],
            'object_id': ['This field may not be null.'],
            'order': ['This field may not be null.'],
            'quantity': ['This field may not be null.']
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_field(self):
        """
        Ensure we can't create an order when requi{
            'object_id': [
                'User does not have the required membership to order this '
                'package.'
            ]
        }red field are invalid.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'content_type': (1,),
            'object_id': "invalid",
            'order': "invalid",
            'quantity': (1,),
        }

        response = self.client.post(
            reverse('orderline-list'),
            data,
            format='json',
        )

        content = {
            'content_type': ['Object with model=[1] does not exist.'],
            'object_id': ['A valid integer is required.'],
            'order': ['Invalid hyperlink - No URL match.'],
            'quantity': ['A valid integer is required.']
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """
        Ensure we can update an order line.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 99,
            'content_type': "package",
            'object_id': self.package.id,
        }

        response = self.client.put(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
            data,
            format='json',
        )

        content = {
            'content_type': 'package',
            'id': self.order_line.id,
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 99,
            'coupon': None,
            'coupon_real_value': 0.0,
            'cost': 99 * self.package.price,
            'url': f'http://testserver/order_lines/{self.order_line.id}',
            'metadata': None,
            'options': [],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_partial(self):
        """
        Ensure we can partially update an order line.
        """
        self.user.membership = self.membership
        self.client.force_authenticate(user=self.user)

        data = {
            'order': reverse('order-detail', args=[self.order.id]),
            'quantity': 9,
        }

        response = self.client.patch(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
            data,
            format='json',
        )

        self.user.membership = None

        content = {
            'content_type': 'package',
            'id': self.order_line.id,
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 9,
            'coupon': None,
            'coupon_real_value': 0.0,
            'cost': 9 * self.package.price,
            'url': f'http://testserver/order_lines/{self.order_line.id}',
            'metadata': None,
            'options': [],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Ensure we can delete an order line.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list(self):
        """
        Ensure we can't list order lines as an unauthenticated user.
        """
        response = self.client.get(
            reverse('orderline-list'),
            format='json',
        )

        data = json.loads(response.content)

        content = {'detail': 'Authentication credentials were not provided.'}

        self.assertEqual(data, content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_owner(self):
        """
        Ensure we can list owned order lines as an authenticated user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('orderline-list'),
            format='json',
        )

        data = json.loads(response.content)

        content = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'content_type': 'package',
                'id': self.order_line.id,
                'object_id': self.package.id,
                'order': f'http://testserver/orders/{self.order.id}',
                'quantity': 1,
                'coupon': None,
                'coupon_real_value': 0.0,
                'cost': self.package.price,
                'options': [],
                'url': f'http://testserver/order_lines/{self.order_line.id}',
                'metadata': None,
            }]
        }

        self.assertEqual(data, content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_admin(self):
        """
        Ensure we can list all order lines as an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('orderline-list'),
            format='json',
        )

        data = json.loads(response.content)

        content = {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'content_type': 'package',
                'id': self.order_line.id,
                'object_id': self.package.id,
                'order': f'http://testserver/orders/{self.order.id}',
                'quantity': 1,
                'coupon': None,
                'coupon_real_value': 0.0,
                'cost': self.package.price,
                'url': f'http://testserver/order_lines/{self.order_line.id}',
                'metadata': None,
                'options': [],
            }, {
                'content_type': 'package',
                'id': self.order_line_admin.id,
                'object_id': self.package.id,
                'order': f'http://testserver/orders/{self.order_admin.id}',
                'quantity': 99,
                'coupon': None,
                'coupon_real_value': 0.0,
                'cost': 99 * self.package.price,
                'metadata': None,
                'options': [],
                'url':
                    f'http://testserver/order_lines/{self.order_line_admin.id}'
            }]
        }

        self.assertEqual(data, content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_unauthenticated(self):
        """
        Ensure we can't read an order line as an unauthenticated user.
        """

        response = self.client.get(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
        )

        content = {'detail': 'Authentication credentials were not provided.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_read_owner(self):
        """
        Ensure we can read an order line owned by an authenticated user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
        )

        content = {
            'content_type': 'package',
            'id': self.order_line.id,
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 1,
            'coupon': None,
            'coupon_real_value': 0.0,
            'cost': self.package.price,
            'url': f'http://testserver/order_lines/{self.order_line.id}',
            'metadata': None,
            'options': [],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_owner_not_owned(self):
        """
        Ensure we can't read an order line not owned by an authenticated user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'orderline-detail',
                kwargs={'pk': 2},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_admin(self):
        """
        Ensure we can read any order line as an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse(
                'orderline-detail',
                args=[self.order_line.id]
            ),
        )

        content = {
            'content_type': 'package',
            'id': self.order_line.id,
            'object_id': self.package.id,
            'order': f'http://testserver/orders/{self.order.id}',
            'quantity': 1,
            'coupon': None,
            'coupon_real_value': 0.0,
            'cost': self.package.price,
            'url': f'http://testserver/order_lines/{self.order_line.id}',
            'metadata': None,
            'options': [],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_non_existent(self):
        """
        Ensure we get not found when asking for an order line that doesn't
        exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'orderline-detail',
                kwargs={'pk': 999},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_list(self):
        """
        Get list of product, get content_type name group by content_type in
        all order line
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse(
                'orderline-list'
            ) + '/product_list',
        )

        content = [
            {
                'name': 'Package',
                'id': 36,
                'detail': True
            }
        ]

        self.assertEqual(json.loads(response.content), content)
