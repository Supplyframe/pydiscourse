import unittest
import mock

from pydiscourse import client


def prepare_response(request):
    # we need to mocked response to look a little more real
    request.return_value = mock.MagicMock(
        headers={"content-type": "application/json; charset=utf-8"}
    )


class ClientBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.host = "testhost"
        self.api_username = "testuser"
        self.api_key = "testkey"

        self.client = client.DiscourseClient(self.host, self.api_username, self.api_key)

    def assertRequestCalled(self, request, verb, url, **params):
        self.assertTrue(request.called)

        args, kwargs = request.call_args

        self.assertEqual(args[0], verb)
        self.assertEqual(args[1], self.host + url)

        parameters = kwargs.get("params")
        headers = kwargs.get("headers")
        self.assertEqual(headers.get("Api-Key"), self.api_key)
        self.assertEqual(headers.get("Api-Username"), self.api_username)
        self.assertEqual(parameters, params)


@mock.patch("requests.request")
class TestUser(ClientBaseTestCase):
    def test_user(self, request):
        prepare_response(request)
        self.client.user("someuser")
        self.assertRequestCalled(request, "GET", "/users/someuser.json")

    def test_user_by_id(self, request):
        prepare_response(request)
        self.client.user_by_id(12345)
        self.assertRequestCalled(request, "GET", "/admin/users/12345.json")

    def test_create_user(self, request):
        prepare_response(request)
        self.client.create_user(
            "Test User", "testuser", "test@example.com", "notapassword"
        )
        self.assertEqual(request.call_count, 2)
        # XXX incomplete

    def test_update_email(self, request):
        prepare_response(request)
        email = "test@example.com"
        self.client.update_email("someuser", email)
        self.assertRequestCalled(
            request, "PUT", "/users/someuser/preferences/email", email=email
        )

    def test_update_user(self, request):
        prepare_response(request)
        self.client.update_user("someuser", a="a", b="b")
        self.assertRequestCalled(request, "PUT", "/users/someuser", a="a", b="b")

    def test_update_username(self, request):
        prepare_response(request)
        self.client.update_username("someuser", "newname")
        self.assertRequestCalled(
            request,
            "PUT",
            "/users/someuser/preferences/username",
            new_username="newname",
        )

    def test_update_avatar_from_url(self, request):
        prepare_response(request)
        avatar_url = "http://placekitten.com/200/300"
        self.client.update_avatar_from_url("someuser", avatar_url)
        self.assertRequestCalled(
            request, "POST", "/users/someuser/preferences/avatar", file=avatar_url
        )

    def test_update_avatar_image(self, request):
        prepare_response(request)
        avatar_url = "http://placekitten.com/200/300"
        self.client.update_avatar_image("someuser", avatar_url)
        self.assertRequestCalled(
            request,
            "POST",
            "/users/someuser/preferences/avatar",
            files={"file": avatar_url},
        )

    def test_toggle_gravatar(self, request):
        prepare_response(request)
        self.client.toggle_gravatar("someuser")
        self.assertRequestCalled(
            request,
            "PUT",
            "/users/someuser/preferences/avatar/toggle",
            use_uploaded_avatar="true",
        )

    def test_toggle_gravatar_false(self, request):
        prepare_response(request)
        self.client.toggle_gravatar("someuser", False)
        self.assertRequestCalled(
            request,
            "PUT",
            "/users/someuser/preferences/avatar/toggle",
            use_uploaded_avatar="false",
        )

    def test_pick_avatar(self, request):
        prepare_response(request)
        self.client.pick_avatar("someuser")
        self.assertRequestCalled(
            request, "PUT", "/users/someuser/preferences/avatar/pick"
        )

    def test_set_preference(self, request):
        prepare_response(request)
        self.client.set_preference("someuser")
        self.assertRequestCalled(request, "PUT", "/users/someuser")

    def test_set_preference_default(self, request):
        prepare_response(request)
        self.client.set_preference()
        self.assertRequestCalled(request, "PUT", "/users/testuser")


@mock.patch("requests.request")
class TestTopics(ClientBaseTestCase):
    def test_hot_topics(self, request):
        prepare_response(request)
        self.client.hot_topics()
        self.assertRequestCalled(request, "GET", "/hot.json")

    def test_latest_topics(self, request):
        prepare_response(request)
        self.client.latest_topics()
        self.assertRequestCalled(request, "GET", "/latest.json")

    def test_new_topics(self, request):
        prepare_response(request)
        self.client.new_topics()
        self.assertRequestCalled(request, "GET", "/new.json")

    def test_topic(self, request):
        prepare_response(request)
        self.client.topic("some-test-slug", 22)
        self.assertRequestCalled(request, "GET", "/t/some-test-slug/22.json")

    def test_topics_by(self, request):
        prepare_response(request)
        r = self.client.topics_by("someuser")
        self.assertRequestCalled(request, "GET", "/topics/created-by/someuser.json")
        self.assertEqual(r, request().json()["topic_list"]["topics"])

    def invite_user_to_topic(self, request):
        prepare_response(request)
        email = "test@example.com"
        self.client.invite_user_to_topic(email, 22)
        self.assertRequestCalled(
            request, "POST", "/t/22/invite.json", email=email, topic_id=22
        )


@mock.patch("requests.request")
class TestAdmin(ClientBaseTestCase):
    def test_site_settings(self, request):
        prepare_response(request)
        self.client.site_settings(enable_forwarded_emails=False)
        self.assertRequestCalled(
            request,
            "PUT",
            "/admin/site_settings/enable_forwarded_emails",
            enable_forwarded_emails=False,
        )

    def test_trust_level(self, request):
        prepare_response(request)
        self.client.trust_level("someuser", 2)
        self.assertRequestCalled(
            request, "PUT", "/admin/users/someuser/trust_level", level=2
        )

    def test_suspend(self, request):
        prepare_response(request)
        self.client.suspend("someuser", 600, "because")
        self.assertRequestCalled(
            request,
            "PUT",
            "/admin/users/someuser/suspend",
            duration=600,
            reason="because",
        )

    def test_users(self, request):
        prepare_response(request)
        self.client.users()
        self.assertRequestCalled(request, "GET", "/admin/users/list/active.json")

    def test_list_users(self, request):
        prepare_response(request)
        self.client.list_users("happy")
        self.assertRequestCalled(request, "GET", "/admin/users/list/happy.json")

    def test_log_out_user(self, request):
        prepare_response(request)
        self.client.log_out_user("someuser")
        self.assertRequestCalled(request, "POST", "/admin/users/someuser/log_out")

    def test_generate_api_key(self, request):
        prepare_response(request)
        self.client.generate_api_key("someuser")
        self.assertRequestCalled(
            request, "POST", "/admin/users/someuser/generate_api_key"
        )

    def test_anonymize_user(self, request):
        prepare_response(request)
        self.client.anonymize_user("someuser")
        self.assertRequestCalled(request, "PUT", "/admin/users/someuser/anonymize")

    def test_delete_user(self, request):
        prepare_response(request)
        self.client.delete_user("someuser")
        self.assertRequestCalled(request, "DELETE", "/admin/users/someuser.json")


@mock.patch("requests.request")
class MiscellaneousTests(ClientBaseTestCase):
    def test_search(self, request):
        prepare_response(request)
        self.client.search("needle")
        self.assertRequestCalled(request, "GET", "/search.json", term="needle")

    def test_categories(self, request):
        prepare_response(request)
        r = self.client.categories()
        self.assertRequestCalled(request, "GET", "/categories.json")
        self.assertEqual(r, request().json()["category_list"]["categories"])
