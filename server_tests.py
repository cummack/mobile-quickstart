import os
import server
import unittest
import tempfile
from twilio import jwt
from xml.etree import ElementTree

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        pass


    def test_welcome_twiml(self):
        """Tests the root '/' URL which should just return a simple Welcome 
        message using TwiML."""

        response = self.app.get('/')
        # The response is XML
        self.assertEqual(response.mimetype, 'application/xml')
        xml_tree = ElementTree.fromstring(response.get_data())

        # With a root tag <Response>
        self.assertEqual(xml_tree.tag, 'Response')

        # Containing one <Say> tag
        say_tags = xml_tree.findall('Say')
        self.assertEqual(len(say_tags), 1)

        # Which greets our caller
        assert 'Welcome' in say_tags[0].text


    def test_token_generation(self):
        """Tests the '/token' URL to ensure that a JWT token is returned that
        at least closely resembles a valid Twilio Capability token."""

        response = self.app.get('/token')
        # The response is plain text
        self.assertEqual(response.mimetype, 'text/plain')

        # And is *probably* a Twilio Capability token
        jwt_body = jwt.decode(response.get_data(), None, False)
        account_sid = jwt_body.get('iss')
        assert account_sid.startswith('AC')


    def test_client_to_phone_twiml(self):
        """Tests '/call' to validate 'Twilio Client => PSTN Phone' call TwiML 
        Generation."""
        
        from_param = 'client:alice'
        to_param = '+15551235555'

        response = self.app.post('/call', data={'From': from_param, 'To': to_param})
        # The response is XML
        self.assertEqual(response.mimetype, 'application/xml')
        xml_tree = ElementTree.fromstring(response.get_data())

        # With a root tag <Response>
        self.assertEqual(xml_tree.tag, 'Response')

        # Containing one <Dial> tag
        dial_tags = xml_tree.findall('Dial')
        self.assertEqual(len(dial_tags), 1)

        # With a valid Caller ID for the PSTN
        self.assertEqual(dial_tags[0].attrib.get('callerId'), server.CALLER_ID)

        # Which itself contains one <Number> tag
        number_tags = dial_tags[0].findall('Number')
        self.assertEqual(len(number_tags), 1)

        # Which dials our intended phone number
        assert to_param in number_tags[0].text


    def test_client_to_client_twiml(self):
        """Tests '/call' to validate 'Twilio Client => Twilio Client' call TwiML 
        Generation."""
        
        from_param = 'client:alice'
        to_param = 'client:bob'

        response = self.app.post('/call', data={'From': from_param, 'To': to_param})
        # The response is XML
        self.assertEqual(response.mimetype, 'application/xml')
        xml_tree = ElementTree.fromstring(response.get_data())

        # With a root tag <Response>
        self.assertEqual(xml_tree.tag, 'Response')

        # Containing one <Dial> tag
        dial_tags = xml_tree.findall('Dial')
        self.assertEqual(len(dial_tags), 1)

        # Which itself contains one <Client> tag
        client_tags = dial_tags[0].findall('Client')
        self.assertEqual(len(client_tags), 1)

        # Which dials our intended Client instance
        # Note that Twilio appends 'client:' to Client names in TwiML requests
        self.assertEqual(to_param, 'client:' + client_tags[0].text)


    def test_phone_to_client_twiml(self):
        """Tests '/call' to validate 'PSTN Phone => Twilio Client' call TwiML 
        Generation."""
        
        from_param = '+15551235555'
        to_param = '+15550005555'

        response = self.app.post('/call', data={'From': from_param, 'To': to_param})
        # The response is XML
        self.assertEqual(response.mimetype, 'application/xml')
        xml_tree = ElementTree.fromstring(response.get_data())

        # With a root tag <Response>
        self.assertEqual(xml_tree.tag, 'Response')

        # Containing one <Dial> tag
        dial_tags = xml_tree.findall('Dial')
        self.assertEqual(len(dial_tags), 1)

        # Which itself contains one <Client> tag
        client_tags = dial_tags[0].findall('Client')
        self.assertEqual(len(client_tags), 1)

        # Which dials our intended Client instance (hard-coded in server)
        self.assertEqual(server.CLIENT, client_tags[0].text)


if __name__ == '__main__':
    unittest.main()