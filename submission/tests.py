# from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from .models import DRMJobTemplate, Script, Parameter, User
from .views import ScriptViewSet

# # Define request factory
# factory = APIRequestFactory()
# Define test API client
# NOTE test API client tests actual routes, while API request factory
# allows to create separated tests
client = APIClient()


# Test script endpoint
class ScriptViewSetTest(TestCase):

    # Set up tests
    def setUp(self):
        # Create a job template
        self.job = DRMJobTemplate.objects.create(name='1_core_local', queue='local', stdout_file='log.o', stderr_file='log.e', cpus_per_task=1)
        # Create a script template
        self.script = Script.objects.create(name='blast', job=self.job, command='blast.sh')
        # Create parameter templates
        Parameter.objects.create(name='query', flag='--query', type=Parameter.Type.STRING.value, private=False, required=True, script=self.script)
        Parameter.objects.create(name='database', flag='--db', type=Parameter.Type.STRING.value, private=False, required=True, script=self.script)
        Parameter.objects.create(name='num_threads', flag='-n', type=Parameter.Type.INTEGER.value, private=True, required=False, script=self.script)

    # Test single script retrieval
    def test_get_script(self):
        # Define GET request, retrieve response
        response = client.get('/script/{0:s}/'.format(self.script.name))
        # Test retrieved response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name', ''), self.script.name)
        self.assertEqual(len(response.data.get('param', [])), 3)

    # Test multiple script retrieval
    def test_get_scripts(self):
        # Make GET request, retrieve response
        response = client.get('/script/')
        # Test retrieved response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 1)


# Test token endpoint
class TokenViewSetTest(TestCase):

    # Define valid ORCID identifier
    username = '0000-0003-1065-588X'
    # Define valid ORCID access token
    secret = '3b391d83-daea-4bd0-82aa-c70d24f21b21'

    # Set up test
    def setUp(self):
        # Define user
        self.user = User.objects.create(username=self.username, source=User.ORCID, active=True)

    # Test token exchange
    def test_get_token(self):
        # Set client authorization token
        client.credentials(HTTP_AUTHORIZATION='Bearer {0:s}'.format(self.secret))
        # Make GET request, retrieve response
        response = client.get('/token/{0:s}/'.format(self.username))
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('access_token', ''), '')
        self.assertEqual(response.data.get('user_name', ''), self.user.username)
        self.assertEqual(response.data.get('user_source', ''), self.user.source)

    # Test token exchange with wrong user
    def test_wrong_user(self):
        # Set client authorization token
        client.credentials(HTTP_AUTHORIZATION='Bearer {0:s}'.format(self.secret))
        # Make GET request, retrieve response
        response = client.get('/token/{0:s}/'.format('this-is-not-an-user'))
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test token exchange with wrong token
    def test_wrong_token(self):
        # NOTE sandbox API always return queried user's record, so
        # this test would pass anyway. This is why it has not been
        # implemented!
        pass


# Test task endpoint
class TaskViewSetTest(TestCase):

    # TODO Set up test
    def setUp(self) -> None:
        raise NotImplementedError

    # TODO Test task lifecycle (submit, status, delete)
    def test_task_lifecycle(self) -> None:
        raise NotImplementedError

    # TODO Test task hierarchy (dependent task must be executed after dependency task)
    def test_task_hierarchy(self) -> None:
        raise NotImplementedError