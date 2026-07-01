# Owner Backend Guide

## What the owner needs to run
The owner is responsible for running the automation backend that processes the booking requests.

## Required setup on the owner side
1. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Make sure the browser is available:
   - Google Chrome or Microsoft Edge should be installed.
3. Set the required environment variables:
   ```powershell
   $env:FLASK_SECRET_KEY="change-this-secret"
   $env:CLIENT_USERNAME="client"
   $env:CLIENT_PASSWORD="change-me"
   ```
4. Start the web app locally:
   ```powershell
   python app.py
   ```
5. Run the booking automation from the backend when a request is received.

## What the owner should do when a client submits a request
1. Review the request from the dashboard.
2. Confirm the preferred centre and email.
3. Run the automation workflow from the backend.
4. Send status updates to the client.
5. Notify the client if a booking is confirmed or if no slot is available.

## Notes
- Keep credentials secure.
- Do not share sensitive login data publicly.
- The backend is the part that performs the actual booking automation.
