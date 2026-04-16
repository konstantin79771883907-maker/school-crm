#!/usr/bin/env python3
"""
GitHub Webhook Handler for Auto-Deploy

This script receives push events from GitHub and automatically:
1. Pulls latest code from the repository
2. Restarts the CRM service

Security: Uses a secret token to verify webhook authenticity.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import hashlib
import hmac
import os
import json

# Configuration - Change this secret!
WEBHOOK_SECRET = "your-secret-token-change-in-production"
REPO_PATH = "/opt/school-crm"
SERVICE_NAME = "school-crm"


class DeployHookHandler(BaseHTTPRequestHandler):
    """HTTP handler for GitHub webhook requests."""

    def do_POST(self):
        """Handle POST requests from GitHub."""
        # Get the signature from headers
        signature = self.headers.get('X-Hub-Signature-256', '')
        
        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)
        
        # Verify the webhook signature
        if not self.verify_signature(signature, payload):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Invalid signature')
            return
        
        # Parse the payload
        data = json.loads(payload.decode('utf-8'))
        
        # Only respond to push events to main branch
        if 'ref' in data and data['ref'] == 'refs/heads/main':
            self.deploy()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Ignored (not main branch)')
            return

    def verify_signature(self, signature, payload):
        """Verify the HMAC signature from GitHub."""
        if not signature:
            return False
        
        expected_signature = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def deploy(self):
        """Execute the deployment process."""
        try:
            # Pull latest changes
            subprocess.run(
                ['git', '-C', REPO_PATH, 'pull'],
                check=True,
                capture_output=True
            )
            
            # Restart the service
            subprocess.run(
                ['systemctl', 'restart', SERVICE_NAME],
                check=True,
                capture_output=True
            )
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Deployment successful')
            
        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Deployment failed: {str(e)}'.encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server(port=8001):
    """Start the webhook server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DeployHookHandler)
    print(f"Deploy hook server running on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
