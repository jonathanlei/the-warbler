"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, Like, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users.
        /login
        /logout
        /users
        /users/{user_id}
        /users/{user_id}/likes
        /users/{user_id}/following
        /users/{user_id}/followers
        /users/{user_id}/follow/{follow_id}
        /users/{user_id}/stop-following/{follow_id}
        /users/profile
        /users/delete
    """


    def setUp(self):
        """Create test client, add sample data."""
        Like.query.delete()
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        u = User.signup(username="testuser",
                        email="test66@test.com",
                        password="testuser",
                        image_url=None)

        db.session.commit()
        self.user_id = u.id

    def tearDown(self):
        """ Rollback transactions """
        db.session.rollback()

    def test_view_login(self):
        """ Test login view. """
        with self.client as c:
            resp = c.post("/login",
                    data={"username":"testuser", "password":"testuser"},
                    follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Hello, testuser", html)


    def test_view_login_bad_username(self):
        """ Test login view. """
        with self.client as c:
            resp = c.post("/login",
                    data={"username":"adsji", "password":"testuser"},
                    follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Invalid credentials", html)


    def test_view_login_bad_password(self):
        """ Test login view. """
        with self.client as c:
            resp = c.post("/login",
                    data={"username":"testuser", "password":"fuklejhefh"},
                    follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Invalid credentials", html)


    def test_view_logout(self):
        """ Test /logout view. """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp1 = c.post("/logout",
                    follow_redirects=True)
            resp = c.get("/users/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)


    def test_view_users(self):
        """ Test /users """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.get("/users", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("users-index", html)


    def test_view_userid(self):
        """ Test /users/{user_id} """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.get(f"/users/{self.user_id}", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Messages", html)
        self.assertIn("Following", html)
        self.assertIn("Followers", html)
        self.assertIn("Likes", html)


    def test_view_likes(self):
        """ Test /users/{user_id}/likes """

    def test_view_following(self):
        """  """

    def test_view_followers(self):
        """  """

    def test_view_follow_id(self):
        """  """

    def test_view_stop_following(self):
        """  """

    def test_view_profile(self):
        """ View the user's profile for editing.
            /users/profile
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.get("/users/profile", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit Your Profile", html)

    def test_edit_profile(self):
        """ View the user's profile for editing.
            /users/profile
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.get("/users/profile", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit Your Profile", html)
        # TODO: submit an edit

    def test_view_delete_user(self):
        """  """
