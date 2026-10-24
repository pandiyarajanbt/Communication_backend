from unittest.mock import Mock, patch

from django.test import TestCase

from candidate.models import Candidate, CandidateMessage
from candidate.schema.query import CandidateQuery
from candidate.schema.query.message import CandidateType
from candidate.whatsapp import send_text


class CandidateSchemaTests(TestCase):
    def test_candidate_type_uses_relay_node_interface(self):
        interfaces = [interface.__name__ for interface in CandidateType._meta.interfaces]
        self.assertIn('Node', interfaces)

    def test_candidate_query_exposes_relay_node_field(self):
        self.assertIn('node', CandidateQuery._meta.fields)

    @patch('candidate.whatsapp.requests.post')
    def test_send_text_stores_candidate_message_history(self, mock_post):
        candidate = Candidate.objects.create(
            full_name='Asha',
            phone_number='919876543210',
            status='not_sent',
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'messages': [{'id': 'wamid.123'}]}
        mock_post.return_value = mock_response

        result = send_text(candidate, 'Hello there')

        self.assertTrue(result['ok'])
        self.assertTrue(CandidateMessage.objects.filter(
            candidate=candidate,
            message_id='wamid.123',
            message='Hello there',
        ).exists())
