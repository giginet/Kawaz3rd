# coding=utf-8
"""
"""

import os
from django.test import TestCase
from unittest.mock import MagicMock
from ..conf import settings
from ..client import (require_enabled,
                      GoogleCalendarClient)


class GoogleCalendarClientRequireEnabledDecoratorTestCase(TestCase):
    def test_require_enabled_call_method(self):
        """
        decorated method should be called if `enabled` is True
        """
        method = MagicMock(return_value=True)
        decorated = require_enabled(method)
        # Mock to behave as the first argument of class method
        _self = MagicMock()
        _self.enabled = True
        self.assertTrue(decorated(_self))
        self.assertTrue(method.called)

    def test_require_enabled_do_not_call_method(self):
        """
        decorated method should not be called if `enabled` is False
        """
        method = MagicMock(return_value=True)
        decorated = require_enabled(method)
        # Mock to behave as the first argument of class method
        _self = MagicMock()
        _self.enabled = False
        self.assertIsNone(decorated(_self))
        self.assertFalse(method.called)


class GoogleCalendarClientTestCaseBase(TestCase):
    def setUp(self):
        self.event = {
            'summary': 'Appointment',
            'location': 'Somewhere',
            'start': {
                'dateTime': '2014-12-03T10:00:00.000-07:00'
            },
            'end': {
                'dateTime': '2014-12-03T10:25:00.000-07:00'
            },
        }
        self.client = GoogleCalendarClient(
            settings.GOOGLE_CALENDAR_CALENDAR_ID
        )


if os.path.exists(settings.GOOGLE_CALENDAR_CREDENTIALS):
    class GoogleCalendarClientTestCase(GoogleCalendarClientTestCaseBase):

        def get_event_status(self, event):
            e = self.client.get(event['id'])
            return e['status']

        def test_insert(self):
            event = self.client.insert(self.event)
            self.assertIsNotNone(event)
            self.assertEqual(event['summary'], 'Appointment')

            # the event entry exists on the web
            self.assertEqual(self.get_event_status(event), 'confirmed')

            # tearDown
            self.client.delete(event['id'])

        def test_patch(self):
            event = self.client.insert(self.event)
            event = self.client.patch(event['id'], {'summary': 'foobar'})
            self.assertEqual(event['summary'], 'foobar')

            # tearDown
            self.client.delete(event['id'])

        def test_delete(self):
            event = self.client.insert(self.event)
            self.client.delete(event['id'])

            # the event entry should not exists on the web
            self.assertEqual(self.get_event_status(event), 'cancelled')
else:
    class GoogleCalendarClientTestCase(GoogleCalendarClientTestCaseBase):
        def setUp(self):
            # disable warnings
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                super().setUp()

        def test_insert(self):
            self.assertIsNone(self.client.insert(self.event))

        def test_patch(self):
            self.assertIsNone(self.client.patch('0', self.event))

        def test_delete(self):
            self.assertIsNone(self.client.delete('0'))
