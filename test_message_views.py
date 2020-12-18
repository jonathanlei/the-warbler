"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Like

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        Like.query.delete()
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_show_message(self):
        """ Can the message page be shown?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            m = Message.query.one()
            resp = c.get(f"/messages/{m.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello", html)
            self.assertIn('id="messages"', html)

            # test for when message id is not found
            resp = c.get("/messages/66666666")
            self.assertEqual(resp.status_code, 404)

    def test_delete_message(self):
        """ Can the user delete its own message? """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            m = Message.query.one()

            resp = c.post(f'/messages/{m.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Hello", html)
            self.assertIn('id="user-show"', html)

            u2 = User.signup(username="testuser2",
                             email="test2@test.com",
                             password="testuser2",
                             image_url=None)
            db.session.commit()
            m2 = Message(text="TestMessage2")
            u2.messages.append(m2)
            db.session.commit()

            resp = c.post(f'/messages/{m2.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_like_and_unlike_warble(self):
        """ Can a user like the warble?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            m = Message.query.one()
            self.assertEqual(Like.query.count(), 0)

            # Test /like view
            resp = c.post( f"/messages/{m.id}/like", follow_redirects=True)
            self.assertEqual(Like.query.count(), 1)
            self.assertEqual(resp.status_code, 200)

            # Test /unlike view
            resp = c.post( f"/messages/{m.id}/unlike", follow_redirects=True)
            self.assertEqual(Like.query.count(), 0)
            self.assertEqual(resp.status_code, 200)
