from datetime import timedelta
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from candidate.models import Candidate, CandidateMessage
from candidate.schema.query import CandidateQuery
from candidate.schema.query.message import CandidateType, _dispatch
from candidate.whatsapp import send_template, send_text


class CandidateSchemaTests(TestCase):
    def test_candidate_type_uses_relay_node_interface(self):
        interfaces = [interface.__name__ for interface in CandidateType._meta.interfaces]
        self.assertIn('Node', interfaces)

    def test_candidate_query_exposes_relay_node_field(self):
        self.assertIn('node', CandidateQuery._meta.fields)

    @patch('candidate.whatsapp.Client')
    def test_send_text_stores_candidate_message_history(self, mock_client):
        candidate = Candidate.objects.create(
            full_name='Asha',
            phone_number='919500525108',
            status='not_sent',
        )

        mock_message = Mock()
        mock_message.sid = 'SM123'
        mock_client.return_value.messages.create.return_value = mock_message

        result = send_text(candidate, 'Hello there')

        self.assertTrue(result['ok'])
        self.assertEqual(result['message_id'], 'SM123')
        self.assertTrue(CandidateMessage.objects.filter(
            candidate=candidate,
            message_id='SM123',
            message='Hello there',
        ).exists())

    @override_settings(TWILIO_WHATSAPP_TEMPLATE_SID='   ')
    @patch('candidate.whatsapp.Client')
    def test_send_template_ignores_blank_template_sid_and_falls_back_to_text(self, mock_client):
        candidate = Candidate.objects.create(
            full_name='Asha',
            phone_number='919500525108',
            status='not_sent',
        )

        mock_message = Mock()
        mock_message.sid = 'SM456'
        mock_client.return_value.messages.create.return_value = mock_message

        result = send_template(candidate, template_name='hello_world', params=['Raj'])

        self.assertTrue(result['ok'])
        self.assertEqual(result['message_id'], 'SM456')
        call_kwargs = mock_client.return_value.messages.create.call_args.kwargs
        self.assertNotIn('content_sid', call_kwargs)
        self.assertIn('body', call_kwargs)
        self.assertIn('Raj', call_kwargs['body'])

    @override_settings(TWILIO_WHATSAPP_TEMPLATE_SID='HX123')
    @patch('candidate.whatsapp.Client')
    def test_dispatch_uses_template_when_message_is_outside_24h_window(self, mock_client):
        candidate = Candidate.objects.create(
            full_name='Asha',
            phone_number='919500525108',
            status='not_sent',
            last_message=timezone.now() - timedelta(days=2),
        )

        mock_message = Mock()
        mock_message.sid = 'SM789'
        mock_client.return_value.messages.create.return_value = mock_message

        result = _dispatch(candidate, 'Hello from Twilio', 'hello_world', None)

        self.assertTrue(result['ok'])
        self.assertEqual(result['message_id'], 'SM789')
        call_kwargs = mock_client.return_value.messages.create.call_args.kwargs
        self.assertIn('content_sid', call_kwargs)
        self.assertEqual(call_kwargs['content_sid'], 'HX123')

    @override_settings(TWILIO_WHATSAPP_TEMPLATE_SID='')
    @patch('candidate.whatsapp.Client')
    def test_dispatch_rejects_freeform_message_without_template_sid(self, mock_client):
        candidate = Candidate.objects.create(
            full_name='Asha',
            phone_number='919500525108',
            status='not_sent',
            last_message=timezone.now() - timedelta(days=2),
        )

        result = _dispatch(candidate, 'Hello from Twilio', 'hello_world', None)

        self.assertFalse(result['ok'])
        self.assertIsNone(result['message_id'])
        self.assertIn('24-hour', result['error'])
        mock_client.return_value.messages.create.assert_not_called()
