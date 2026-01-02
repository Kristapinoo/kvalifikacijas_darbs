# Mācību materiālu ģenerēšanas sistēma ar MI integrāciju

Web aplikācija skolotājiem automātiskai testu un mācību materiālu ģenerēšanai, izmantojot Claude AI.

## Tehnoloģijas

**Backend:**
- Python 3.8+ (Flask framework)
- SQLite database
- Claude API (Anthropic)

**Frontend:**
- React + TypeScript
- Vite

## Instalācija

### 1. Backend

```bash
# Pāriet uz backend direktoriju
cd backend

# Izveido Python virtual environment
python3 -m venv venv

# Aktivizē virtual environment
source venv/bin/activate

# Instalē dependencies
pip install -r requirements.txt

# Izveido .env failu
cp .env.example .env

# Rediģē .env un pievieno savas API atslēgas:
# - FLASK_SECRET_KEY (jebkura nejauša virkne)
# - CLAUDE_API_KEY (no https://console.anthropic.com/)

# Izveido datu bāzi
python init_db.py
```

### 2. Frontend

```bash
# Pāriet uz frontend direktoriju
cd frontend

# Instalē dependencies
npm install
```

## Palaišana

### Visu uzreiz (backend + frontend)
```bash
npm run dev
```

### Vai atsevišķi:

**Backend serveri:**
```bash
npm run dev:backend
```
Servera adrese: **http://localhost:5000**

**Frontend aplikāciju:**
```bash
npm run dev:frontend
```
Frontend adrese: **http://localhost:5173**

## Testēšana

### Backend testi

Palaist visus testus:
```bash
npm test
```

### API pārbaude

Pārbaudīt vai backend darbojas:
```bash
curl http://localhost:5000/api/health
```

Atbildei jābūt:
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### Frontend testi

Pārbaudīt TypeScript tipus:
```bash
npm run test:types
```

Pārbaudīt lint kļūdas:
```bash
npm run lint
```

## Datu bāzes struktūra

Sistēma izmanto 6 tabulas:
1. **users** - lietotāju konti
2. **tests** - izveidotie testi
3. **study_materials** - mācību materiāli
4. **assignments** - testa uzdevumi
5. **questions** - jautājumi
6. **question_options** - atbilžu varianti

### Datu bāzes komandas

Izveidot datu bāzi (ja vēl nepastāv):
```bash
npm run init-db
```

Pilnībā atiestatīt datu bāzi (DZĒŠ VISUS DATUS):
```bash
npm run reset-db
```
**Brīdinājums:** `reset-db` izdzēsīs visus lietotājus, testus un materiālus!

Apskatīt datu bāzes saturu:
```bash
npm run view-db
```

## Autors

Kristaps Kostukevičs (kk23156)
Kvalifikācijas darbs - 2026
