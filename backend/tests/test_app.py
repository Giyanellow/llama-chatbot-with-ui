import json

class TestSessionEndpoints:
    def test_get_session_id(self, client):
        """Test that the get_session_id endpoint returns a session ID"""
        
        response = client.get('/api/get_session_id')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'session_id' in data

class TestMessageHistoryEndpoints:
    def test_get_message_history_no_session_id(self, client):
        """Test that the get_message_history endpoint returns an error if no session_id is provided"""
        
        response = client.post('/api/get_message_history', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Missing 'session_id' parameter"

    def test_get_message_history_with_session_id(self, client):
        """Test that the get_message_history endpoint returns a list of messages"""
        
        response = client.get('/api/get_session_id')
        session_id = json.loads(response.data)['session_id']

        response = client.post('/api/get_message_history', json={'session_id': session_id})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'messages' in data

    def test_get_message_history_invalid_session_id(self, client):
        """Test that the get_message_history endpoint returns an error for an invalid session_id"""
        
        response = client.post('/api/get_message_history', json={'session_id': 'invalid_session_id'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == "Invalid session_id: invalid_session_id"

class TestSendMessageEndpoints:
    def test_send_message_no_prompt(self, client):
        """Test that the send_message endpoint returns an error if no prompt is provided"""
        
        response = client.post('/api/send_message', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Missing 'prompt' parameter"

    def test_send_message_with_prompt(self, client):
        """Test that the send_message endpoint returns a message"""
        
        response = client.get('/api/get_session_id')
        session_id = json.loads(response.data)['session_id']

        response = client.post('/api/send_message', json={'message': 'Hello', 'session_id': session_id})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

    def test_send_message_invalid_session_id(self, client):
        """Test that the send_message endpoint returns an error for an invalid session_id"""
        
        response = client.post('/api/send_message', json={'message': 'Hello', 'session_id': 'invalid_session_id'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Invalid session_id: invalid_session_id"

    def test_send_message_empty_message(self, client):
        """Test that the send_message endpoint returns an error for an empty message"""
        
        response = client.get('/api/get_session_id')
        session_id = json.loads(response.data)['session_id']

        response = client.post('/api/send_message', json={'message': '', 'session_id': session_id})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Missing 'prompt' parameter"