"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """ Rollback transactions """
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        # check repr method
        self.assertEqual(u.__repr__(),
                         f"<User #{u.id}: testuser, test@test.com>")

    def test_user_follow(self):
        """ Does the is_following and is_followed_by work?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        #u1 follows u2, u2 doesn't follow u1
        follow = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_following(u1), False)
        self.assertEqual(u2.is_followed_by(u1), True)
        self.assertEqual(u1.is_followed_by(u2), False)
        # delete u1 following u2
        # print(type(u1.id), u1.id)
        follow = Follows.query.get((u2.id, u1.id))
        db.session.delete(follow)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_following(u1), False)
        self.assertEqual(u2.is_followed_by(u1), False)
        self.assertEqual(u1.is_followed_by(u2), False)

    def test_user_register(self):
        """ Can we create new users?"""

        new_user = User.signup(username="new.user",
                               email="new.user@register.com",
                               password="HASH_THIS_PASS",
                               image_url="https://vignette.wikia.nocookie.net/questionablecontent/images/7/7a/Yelling_Bird.png/revision/latest?cb=20100107084653")
        # print(new_user)
        db.session.commit()

        self.assertIsNotNone(new_user.id)
        self.assertEqual(f"{new_user}",
                         f"<User #{new_user.id}: new.user, new.user@register.com>")

    def test_user_register_validation(self):
        """ Can we create new users?"""

        new_user = User.signup(username="new.user",
                               email="new_user@test.com",
                               password="HASH_THIS_PASS",
                               image_url="https://vignette.wikia.nocookie.net/questionablecontent/images/7/7a/Yelling_Bird.png/revision/latest?cb=20100107084653")

        new_user = User.signup(username="new.user",
                               email="new_user@test.com",
                               password="HASH_THIS_PASS",
                               image_url=None)
        try:
            db.session.commit()
        except IntegrityError as e:
            # print(e)
            self.assertIn("duplicate key value violates unique constraint \"users_email_key\"", f"{e}")
            self.assertIsNone(new_user.id)
            self.assertNotEqual(f"{new_user}",
                f"<User #{new_user.id}: new.user, new.user@register.com>")

    def test_user_authentication(self):
        """ Can we login as a user?"""
        user = self._create_test_user()
        auth = User.authenticate("testuser42", "HASHED_PASSWORD")
        # print("AUTH:",auth)
        self.assertNotEqual(auth, False)
        self.assertEqual(f"{auth}",
                         f"<User #{auth.id}: testuser42, test_42@test.com>")

    def test_user_authentication_bad_username(self):
        """ Will a bad username fail to create user? """
        user = self._create_test_user()
        # print(user)
        auth = User.authenticate("fails", "HASHED_PASSWORD")
        # print("AUTH:",auth)
        self.assertEqual(auth, False)

    def test_user_authentication_bad_password(self):
        """ Will a bad password fail to create user? """
        user = self._create_test_user()
        # print(user)
        auth = User.authenticate("testuser42", "PASSWORD_fails")
        # print("AUTH:",auth)
        self.assertEqual(auth, False)

    def _create_test_user(self):
        """ Create user to login with. """
        u = User.signup(
                email="test_42@test.com",
                username="testuser42",
                password="HASHED_PASSWORD",
                image_url="https://vignette.wikia.nocookie.net/questionablecontent/images/7/7a/Yelling_Bird.png/revision/latest?cb=20100107084653"
        )
        db.session.add(u)
        db.session.commit()
        return u
