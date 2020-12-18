"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, Like, Message, Follows

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

db.drop_all()
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
        Follows.query.delete()
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
                          data={"username": "testuser", "password": "testuser"},
                          follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Hello, testuser", html)

    def test_view_login_bad_username(self):
        """ Test login view. """
        with self.client as c:
            resp = c.post("/login",
                          data={"username": "adsji", "password": "testuser"},
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
            c.post("/logout", follow_redirects=True)
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
        self.assertIn('id="users-index"', html)

    def test_view_userid(self):
        """ Test /users/{user_id} """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.get(f"/users/{self.user_id}", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user-details"', html)

    def test_view_likes(self):
        """ Test /users/{user_id}/likes """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        resp = c.get(f"/users/{self.user_id}/likes")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="liked-messages"', html)

    def test_view_following(self):
        """ Test /users/{user_id}/following """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        resp = c.get(f"/users/{self.user_id}/following")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="following"', html)

    def test_view_followers(self):
        """ Test /users/{user_id}/followers """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        resp = c.get(f"/users/{self.user_id}/followers")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="followers"', html)

    def test_view_follow_id(self):
        """ Test Follow another user  """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        # helper
        u2 = User.signup(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                         image_url=None)
        db.session.commit()

        resp = c.post(f"/users/follow/{u2.id}", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="following"', html)
        self.assertIn("testuser2", html)

    def test_view_stop_following(self):
        """ Test stop following """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        #helper
        u2 = User.signup(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                         image_url=None)
        db.session.commit()
        u2_id = u2.id
        c.post(f"/users/follow/{u2_id}", follow_redirects=True)

        resp = c.post(f"/users/stop-following/{u2_id}", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="following"', html)
        self.assertNotIn("testuser2", html)

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
        #

    def test_edit_profile(self):
        """ View the user's profile for editing.
            /users/profile
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.post("/users/profile",
                      data={
                            "username": "testUserEdit",
                            "email": "testEdit@test.com",
                            "location": "WarbleNest",
                            "bio": "Warbles are the best",
                            "password": "testuser"},
                      follow_redirects=True)
  
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id="user-details"', html)
        self.assertIn("testUserEdit", html)
        self.assertIn("Warbles are the best", html)
        self.assertIn("WarbleNest", html)

    def test_edit_profile_wrong_password(self):
        """ Test editing the profile with wrong pw,
        should redirect to homepage
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        resp = c.post("/users/profile",
                      data={
                            "username": "testUserEdit",
                            "email": "testEdit@test.com",
                            "location": "WarbleNest",
                            "bio": "Warbles are the best",
                            "password": "WRONG PASSWORD"},
                      follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Password Incorrect.", html)

    def test_edit_profile_field_missing(self):
        """ Test editing the profile with missing fields,
        should redirect to edit form
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        resp = c.post("/users/profile",
                      data={
                            "username": "testUserEdit",
                            "password": "testuser"},
                      follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Edit Your Profile.", html)
        self.assertIn("This field is required.", html)

    def test_view_delete_user(self):
        """ Test deleting user route,
        should redirect to sign up page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
        resp = c.post("/users/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIsNone(User.query.get(self.user_id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Join Warbler today.", html)
