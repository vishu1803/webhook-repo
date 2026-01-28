# GitHub Webhook System

A complete end-to-end GitHub webhook system built for a hiring assessment.

## 🏗️ System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌────────────────┐
│   GitHub Repo   │────▶│  Flask Backend   │────▶│   MongoDB   │◀────│ Next.js UI     │
│  (action-repo)  │     │    /webhook      │     │github_events│     │ Polls /events  │
└─────────────────┘     └──────────────────┘     └─────────────┘     └────────────────┘
```

**Data Flow:**
1. GitHub Event → User performs action (push/PR/merge) on `action-repo`
2. Webhook Trigger → GitHub sends POST to Flask `/webhook` endpoint
3. Data Extraction → Flask extracts only required fields (no raw payload stored)
4. MongoDB Insert → Event stored with duplicate prevention via unique index
5. UI Polling → Next.js polls `/events` every 15 seconds
6. Display → New events rendered with proper formatting

## 📁 Project Structure

```
webhook-repo/
├── backend/                # Flask Backend
│   ├── app/
│   │   ├── __init__.py    # App factory
│   │   ├── config.py      # Configuration
│   │   ├── models/        # Event model
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── utils/         # Database utilities
│   ├── requirements.txt
│   ├── run.py             # Entry point
│   └── .env
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Pages and layout
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── lib/           # Utilities and types
│   ├── package.json
│   └── .env.local
│
└── README.md
```

## 🗃️ MongoDB Schema

**Collection:** `github_events`

```javascript
{
  _id: ObjectId,              // MongoDB auto-generated
  request_id: string,         // UNIQUE - Commit hash (PUSH) or PR ID
  author: string,             // GitHub username
  action: string,             // Enum: "PUSH", "PULL_REQUEST", "MERGE"
  from_branch: string,        // Source branch
  to_branch: string,          // Target branch
  timestamp: datetime         // UTC datetime
}
```

**Indexes:**
- `request_id` - Unique index (prevents duplicates)
- `timestamp` - Descending index (efficient sorting)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB (local or Atlas)
- Git

### 1. Clone and Setup Backend

```bash
cd webhook-repo/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python run.py
```

Backend will be running on: `http://localhost:5000`

### 2. Setup Frontend

```bash
cd webhook-repo/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running on: `http://localhost:3000`

### 3. Configure GitHub Webhook

1. Create a repository called `action-repo` on GitHub
2. Go to Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL:** Your public backend URL (e.g., using ngrok)
   - **Content type:** `application/json`
   - **Events:** Select "Pushes" and "Pull requests"
4. Save the webhook

### 4. Expose Local Backend (for GitHub webhooks)

```bash
# Install ngrok
# Windows: Download from https://ngrok.com
# Then run:
ngrok http 5000
```

Use the ngrok URL (e.g., `https://abc123.ngrok.io/webhook`) as your webhook URL in GitHub.

## 📡 API Endpoints

### POST `/webhook`
Receives GitHub webhook payloads.

**Headers:**
- `X-GitHub-Event`: Event type (push, pull_request)
- `Content-Type`: application/json

**Response:**
```json
{
  "status": "success",
  "message": "PUSH event saved successfully",
  "request_id": "abc123..."
}
```

### GET `/events`
Fetches events for UI display.

**Query Parameters:**
- `since` (optional): ISO timestamp to fetch events after
- `all` (optional): If "true", fetch all events

**Response:**
```json
{
  "status": "success",
  "events": [...],
  "count": 5,
  "last_timestamp": "2024-01-26T15:30:00Z",
  "total_in_db": 25
}
```

### GET `/health`
Health check endpoint.

## 🎨 UI Display Formats

- **PUSH:** `"{author} pushed to {to_branch} on {timestamp}"`
- **PULL_REQUEST:** `"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"`
- **MERGE:** `"{author} merged branch {from_branch} to {to_branch} on {timestamp}"`

