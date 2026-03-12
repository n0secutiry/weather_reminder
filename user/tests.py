from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegisterTest(APITestCase):
    def test_successful_register(self):
        data = {
            'email': 'gmail_for_test@gmail.com',
            'password': 'h^12328^5g2gt$512f9dx5$123j',
            'confirm_password': 'h^12328^5g2gt$512f9dx5$123j'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='gmail_for_test@gmail.com').exists())
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "User registered successfully")

    def test_do_not_match_password(self):
        data = {
            'email': 'gmail_for_test@gmail.com',
            'password': '12312312312312',
            'confirm_password': 'j^^&123)9*88u'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='gmail_for_test@gmail.com').exists())
        self.assertIn('password', response.data)
        self.assertIn("Password fields didn't match.", response.data['password'])

    def test_not_valid_mail(self):
        data = {
            'email': 'gmail_for_test',
            'password': '12312312312312',
            'confirm_password': 'j^^&123)9*88u'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='gmail_for_test@gmail.com').exists())
        self.assertIn('email', response.data)
        self.assertIn('Enter a valid email address.', response.data['email'])


class UserLoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test_mail_for_test_login@gmail.com',
            password='mypasswordfortestlogin'
        )

    def test_success_login(self):
        data = {
            'email': 'test_mail_for_test_login@gmail.com',
            'password': 'mypasswordfortestlogin'
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_unsuccess_login(self):
        data = {
            'email': 'testmailwrong',
            'password': 'test_test_test'
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('No active account found with the given credentials', response.data['detail'])

    def test_unsuccess_login_blank_password(self):
        data = {
            'email': 'test_mail_for_test_login@gmail.com',
            'password': ''
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['password'])

    def test_unsuccess_login_blank_email(self):
        data = {
            'email': '',
            'password': '123123213213'
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['email'])

    def test_unsucces_login_blank_creds(self):
        data = {
            'email': '',
            'password': ''
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['email'])
        self.assertIn('This field may not be blank.', response.data['password'])

    def test_successful_refresh_token(self):
        data = {
            'email': 'test_mail_for_test_login@gmail.com',
            'password': 'mypasswordfortestlogin'
        }
        response = self.client.post(reverse('token_obtain_pair'), data, format='json')
        jwt_token = response.data['refresh']
        
        data_for_refresh = {'refresh': jwt_token}
        response_for_refresh = self.client.post(reverse('token_refresh'), data_for_refresh, format='json')
        
        self.assertEqual(response_for_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', response_for_refresh.data)

    def test_unsuccessful_refresh_token(self):
        data = {'refresh': 'qweejejjencjjewjeejwrj'}
        response = self.client.post(reverse('token_refresh'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Token is invalid', response.data['detail'])
        self.assertIn('token_not_valid', response.data['code'])


class CityWeatherTest(APITestCase):
    def setUp(self):
        self.email = 'test_mail_for_test@gmail.com'
        self.password = 'wqeqweqe(7#12)'
        self.test_user = User.objects.create_user(
            email=self.email,
            password=self.password
        )
        
        login_response = self.client.post(reverse('token_obtain_pair'), {
            'email': self.email,
            'password': self.password
        }, format='json')
        
        self.token = login_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_all_city(self):
        self.client.post(reverse('city_weather'), {'name': 'Kyiv'}, format='json')
        self.client.post(reverse('city_weather'), {'name': 'New+York'}, format='json')
        self.client.post(reverse('city_weather'), {'name': 'Miami'}, format='json')

        response = self.client.get(reverse('city_weather'), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Kyiv', response.data[0]["name"])
        self.assertIn('New York', response.data[1]["name"])
        self.assertIn('Miami', response.data[2]["name"])
        self.assertIn('lat', response.data[0])
        self.assertIn('lon', response.data[0])
        self.assertIn('temperature', response.data[0])

    def test_create_subscribe_city(self):
        response = self.client.post(reverse('city_weather'), {'name': 'New York'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('city_details', response.data)

    def test_invalid_data_for_subscribe(self):
        response = self.client.post(reverse('city_weather'), {'name': '122131323'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn("City not found", response.data["error"])

    def test_unscribe_city(self):
        self.client.post(reverse('city_weather'), {'name': 'Kyiv'}, format='json')
        
        response = self.client.delete(reverse('city_weather'), {'name': 'Kyiv'}, format='json')
        
        user = User.objects.get(email=self.email)
        self.assertFalse(user.cities.filter(name="Kyiv").exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('successful', response.data)
        self.assertIn('City unsubscribed.', response.data['successful'])

    def test_invalid_unscribe_city(self):
        response = self.client.delete(reverse('city_weather'), {'name': 'NoCityName'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('City not found in DB', response.data['error'])

    def test_update_time_mailing(self):
        response = self.client.patch(reverse('city_weather'), {'interval': 1}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email=self.email, mailing_interval=1).exists())
        self.assertIn('successful', response.data)
        self.assertEqual(response.data['successful'], 'User settings updated successfully!')

    def test_invalid_update_time_mailing(self):
        response = self.client.patch(reverse('city_weather'), {'interval': 'not_integer'}, format='json')
        user = User.objects.get(email=self.email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(user.mailing_interval, 24)

    def test_update_webhook_url(self):
        data = {'webhook_url': 'https://my-test-webhook.com/api'}
        response = self.client.patch(reverse('city_weather'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(email=self.email)
        self.assertEqual(user.webhook_url, 'https://my-test-webhook.com/api')
        self.assertEqual(response.data['successful'], 'User settings updated successfully!')

    def test_update_both_interval_and_webhook(self):
        data = {
            'interval': 12,
            'webhook_url': 'https://another-hook.com/'
        }
        response = self.client.patch(reverse('city_weather'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(email=self.email)
        self.assertEqual(user.mailing_interval, 12)
        self.assertEqual(user.webhook_url, 'https://another-hook.com/')

    def test_invalid_interval_choice(self):
        data = {'interval': 5}
        response = self.client.patch(reverse('city_weather'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid interval', response.data['error'])

    def test_patch_without_valid_fields(self):
        data = {'some_random_field': 'value'}
        response = self.client.patch(reverse('city_weather'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No valid fields provided to update')