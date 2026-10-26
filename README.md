# Communication Backend

A Django-based backend for managing candidates and sending WhatsApp messages via Twilio. It exposes a GraphQL API and supports user authentication with JWT and OTP via email.

---

## Tech Stack

- Python 3.10+
- Django 4.2+
- GraphQL via `graphene-django`
- JWT auth via `django-graphql-jwt`
- WhatsApp messaging via Twilio
- Email (SMTP) for OTP
- SQLite (default, swappable to PostgreSQL)

---

## Project Structure

```
Communication_backend/
├── hunar/              # Django project config (settings, urls, schema)
├── users/              # Custom user model, auth mutations (register, login, OTP)
├── candidate/          # Candidate model, WhatsApp messaging logic, GraphQL schema
├── lib/                # Shared utilities (choices)
├── templates/          # GraphiQL template
├── manage.py
├── requirement.txt
├── .env                # Your local env vars (never commit this)
└── .env.example        # Demo env vars template
```

---

## Step 1 — Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd Communication_backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirement.txt
```

---

## Step 2 — Configure Environment Variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `EMAIL_HOST` | SMTP server host |
| `EMAIL_HOST_USER` | SMTP email address |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID from console.twilio.com |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | Your Twilio WhatsApp sender (e.g. `whatsapp:+1xxxxxxxxxx`) |
| `TWILIO_WHATSAPP_TEMPLATE_SID` | Optional — Twilio content template SID |

---

## Step 3 — Run Migrations

```bash
python manage.py migrate
```

---

## Step 4 — Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

## Step 5 — Start the Server

```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

GraphQL playground: `http://127.0.0.1:8000/graphql/`

Django admin: `http://127.0.0.1:8000/admin/`

---

## GraphQL API

All operations are available at `/graphql/`.

### Auth — Register a User

```graphql
mutation {
  registerUser(email: "user@example.com", password: "yourpassword") {
    token
    user {
      id
      email
    }
  }
}
```

### Auth — Login with Password

```graphql
mutation {
  loginUser(email: "user@example.com", password: "yourpassword") {
    token
    user {
      id
      email
    }
  }
}
```

### Auth — Login with OTP (2-step)

Step 1 — Request OTP (sent to email):

```graphql
mutation {
  sendOtp(email: "user@example.com") {
    success
    message
  }
}
```

Step 2 — Login with OTP:

```graphql
mutation {
  loginUser(email: "user@example.com", otp: "123456") {
    token
    user {
      id
      email
    }
  }
}
```

> All protected mutations require the JWT token in the request header:
> `Authorization: JWT <your-token>`

---

### Candidates — Create

```graphql
mutation {
  createCandidate(fullName: "John Doe", phoneNumber: "919876543210") {
    candidate {
      candidateId
      fullName
      phoneNumber
      status
    }
  }
}
```

> Phone number format: country code + number, no `+` (e.g. `919876543210` for India)

### Candidates — List

```graphql
query {
  allCandidates {
    candidateId
    fullName
    phoneNumber
    status
    lastMessage
  }
}
```

### Candidates — Delete

```graphql
mutation {
  deleteCandidate(candidateId: 1) {
    ok
  }
}
```

---

### WhatsApp — Send to Single Candidate

```graphql
mutation {
  sendWhatsappMessage(candidateId: 1, message: "Hello, your interview is scheduled.") {
    ok
    messageId
    error
  }
}
```

### WhatsApp — Send Bulk

```graphql
mutation {
  sendWhatsappBulk(candidateIds: [1, 2, 3], message: "Reminder: Interview tomorrow.") {
    results {
      candidateId
      ok
      error
    }
  }
}
```

---

## Message Status Values

| Status | Meaning |
|---|---|
| `not_sent` | Default, message not sent yet |
| `send` | Message sent successfully |
| `received` | Delivered to recipient |
| `read` | Read by recipient |
| `failed` | Sending failed |

---

## Notes

- `.env` is gitignored — never commit real credentials
- Use `.env.example` as a reference for other developers
- For production, set `DEBUG=False` and configure a real database (PostgreSQL recommended)
