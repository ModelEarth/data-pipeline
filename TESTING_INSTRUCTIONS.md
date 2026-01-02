# Flask Server Integration Testing Instructions

Follow these steps to test the Flask server integration with the Data Pipeline Admin interface.

## Prerequisites

- Python 3 installed
- Access to the `data-pipeline` directory
- Web browser (Chrome, Firefox, Safari, etc.)

## Step 1: Install Flask Dependencies

Open a terminal and run:

```bash
cd /Users/noor/Documents/model.earth/data-pipeline
pip3 install flask flask-cors
```

**Expected output:** Should show successful installation messages.

**Screenshot needed:** Terminal showing successful installation

---

## Step 2: Verify Flask Server File Exists

Check that the Flask server file exists:

```bash
ls -la flask_server.py
```

**Expected output:** Should show `flask_server.py` file

**Screenshot needed:** Terminal showing the file exists

---

## Step 3: Start the Flask Server

In the terminal, run:

```bash
python3 flask_server.py
```

**Expected output:** You should see:
```
Starting Flask server for Data Pipeline Admin...
Server will run on http://localhost:5000
Health check: http://localhost:5000/health
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Important:** Keep this terminal window open - the Flask server needs to keep running.

**Screenshot needed:** Terminal showing Flask server running

---

## Step 4: Test Flask Health Check (Terminal)

Open a **NEW terminal window** (keep Flask server running in the first one) and test the health endpoint:

```bash
curl http://localhost:5000/health
```

**Expected output:** JSON response like:
```json
{
  "status": "ok",
  "service": "data-pipeline-flask-server",
  "port": 5000,
  "timestamp": "2025-12-18T..."
}
```

**Screenshot needed:** Terminal showing successful curl response

---

## Step 5: Test Flask Health Check (Browser)

Open your web browser and navigate to:

```
http://localhost:5000/health
```

**Expected output:** Should see the same JSON response in the browser

**Screenshot needed:** Browser showing JSON health check response

---

## Step 6: Open Admin Page

Navigate to the admin page in your browser:

```
http://localhost:8887/data-pipeline/admin/
```

**Expected behavior:**
- If Flask is detected: No orange banner should appear
- If Flask is NOT detected: Orange banner saying "Flask Server is not running on port 5000" with "Activate Flask Server" link

**Screenshot needed:** Admin page showing Flask detection status

---

## Step 7: Test Flask Availability Detection

**If you see the orange banner:**
- Click "Retry Check" button
- The banner should disappear if Flask is running

**If you DON'T see the orange banner:**
- Flask is detected correctly ✓

**Screenshot needed:** Admin page after Flask detection check

---

## Step 8: Select a Test Node

In the admin page:
1. Click on a node from the list (try `prod_002` - EPD Emissions Analyzer - it's faster than `prod_001`)
2. The node detail panel should open

**Screenshot needed:** Node detail panel open showing node information

---

## Step 9: Verify "Run Process" Button

In the node detail panel:
1. Scroll to the "Python Command" section
2. Look for the "▶️ Run Process" button
3. Check if there's a message saying "✓ Using Flask server (port 5000)" (if Flask is available)

**Expected:** Button should be enabled and show Flask status

**Screenshot needed:** Node detail panel showing Run Process button and Flask status

---

## Step 10: Test Running a Node (Small Test First)

**IMPORTANT:** Start with a small, fast node to test:

1. Select node `prod_002` (EPD Emissions Analyzer) - this is medium speed and doesn't require API keys
2. Click "▶️ Run Process" button
3. Watch for:
   - Button changes to "🔄 Running..."
   - Status message appears
   - After completion: "✅ Success" or "❌ Failed"

**Expected:** Should execute via Flask API and show results

**Screenshot needed:** 
- Before clicking (showing button)
- During execution (showing "Running...")
- After completion (showing success/failure and output)

---

## Step 11: Test Flask API Directly (Optional)

In a new terminal, test the Flask API directly:

```bash
curl -X POST http://localhost:5000/api/nodes/run \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "prod_002",
    "command": "python analyze_emissions_data.py",
    "working_directory": "../products/pull"
  }'
```

**Expected:** JSON response with execution results

**Screenshot needed:** Terminal showing curl response

---

## Step 12: Test Node Status Endpoint (For Long-Running Tasks)

If you run a long-running task, you can check its status:

```bash
curl http://localhost:5000/api/nodes/prod_001/status
```

**Expected:** Status information about the running process

**Screenshot needed:** Terminal showing status response

---

## Step 13: Test Setup Instructions Page

Navigate to:

```
http://localhost:8887/cloud/run/
```

**Expected:** Should see Flask setup instructions page

**Screenshot needed:** Browser showing setup instructions page

---

## Step 14: Test Flask Unavailable State

1. Stop the Flask server (Ctrl+C in the Flask server terminal)
2. Refresh the admin page
3. **Expected:** Orange banner should appear saying Flask is not running

**Screenshot needed:** Admin page showing Flask unavailable banner

---

## Step 15: Test Next.js API Fallback

With Flask server stopped:
1. Try clicking "Run Process" on a node
2. **Expected:** Should fall back to Next.js API (may show warning message)

**Screenshot needed:** Node detail panel showing fallback behavior

---

## Step 16: Restart Flask and Verify

1. Start Flask server again: `python3 flask_server.py`
2. Refresh admin page
3. **Expected:** Banner should disappear, Flask should be detected

**Screenshot needed:** Admin page showing Flask available again

---

## Testing Checklist

- [ ] Flask dependencies installed
- [ ] Flask server starts successfully
- [ ] Health check endpoint works (curl)
- [ ] Health check endpoint works (browser)
- [ ] Admin page detects Flask when running
- [ ] Admin page shows banner when Flask stopped
- [ ] "Run Process" button works via Flask
- [ ] Node execution completes successfully
- [ ] Setup instructions page accessible
- [ ] Fallback to Next.js API works when Flask unavailable

---

## Troubleshooting

If Flask server won't start:
- Check if port 5000 is already in use: `lsof -i :5000`
- Try a different port (modify flask_server.py)

If admin page can't connect:
- Check browser console for CORS errors
- Verify Flask is running on 127.0.0.1:5000 (not 0.0.0.0)
- Check firewall settings

If "Run Process" doesn't work:
- Check browser console for errors
- Verify node has `run_process_available=yes` in nodes.csv
- Check Flask server terminal for error messages

---

## Notes

- Keep Flask server terminal open while testing
- For very_slow processes (like prod_001), they run in background - check status endpoint
- Auto-commit workflow will only trigger if `auto_commit=yes` in nodes.csv and target_repo is set

