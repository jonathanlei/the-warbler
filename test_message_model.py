"""Message model tests."""


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows, Like


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
        Like.query.delete()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.user = u
        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(text='testText',
                    user_id=f'{self.user.id}')

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(m.user, self.user)
        self.assertEqual(f"{m}",
                         f"Message: {m.id}, testText, {self.user.id}")

    def test_message_like(self):
        """ Does the like relationship work? """

        u2 = self._create_test_user()
        m2 = Message(text='testText2')
        u2.messages.append(m2)
        db.session.commit()

        self.user.liked_messages.append(m2)
        db.session.commit()

        like = Like.query.get((self.user.id, m2.id))

        self.assertEqual(len(self.user.liked_messages), 1)
        self.assertEqual(like.user_id, self.user.id)
        self.assertEqual(like.msg_id, m2.id)
        # delete the like
        Like.query.filter(Like.user_id == self.user.id,
                          Like.msg_id == m2.id).delete()
        db.session.commit()
        self.assertEqual(len(self.user.liked_messages), 0)
        self.assertEqual(len(Like.query.all()), 0)

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
