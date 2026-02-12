# Render Environment Configuration

This document lists all environment variables that need to be configured on Render for the AI Tutor application.

## Required Environment Variables

### Flask Configuration
| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | (generate secure key) | Flask secret key for sessions |

### Google OAuth
| Variable | Value | Description |
|----------|-------|-------------|
| `GOOGLE_CLIENT_ID` | From Google Cloud Console | OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console | OAuth 2.0 Client Secret |
| `GOOGLE_REDIRECT_URI` | `https://your-app.onrender.com/auth/google/callback` | OAuth callback URL |

### Database
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | From Render PostgreSQL | PostgreSQL connection string |

### MiniMax AI API (CRITICAL)
| Variable | Value | Description |
|----------|-------|-------------|
| `MINIMAX_API_KEY` | `sk-cp-MLTikfWSkQ0x2jepKdyGY2ZwLqmeQUyo5pp2Qp5R0AEOgcxxwegozaB9m7GnYePnZZW6LTb1oWjbazRIRBuvNj8_D66-2qrG8H_oA2ebWYhE5LZBkYy7NxQ` | **AI content generation** |
| `MINIMAX_BASE_URL` | `https://api.minimax.chat/v1` | API endpoint |

### Optional (for TTS)
| Variable | Value | Description |
|----------|-------|-------------|
| `R2_ACCOUNT_ID` | From Cloudflare | For audio file storage |
| `R2_ACCESS_KEY_ID` | From Cloudflare | R2 access key |
| `R2_SECRET_ACCESS_KEY` | From Cloudflare | R2 secret key |
| `R2_BUCKET_NAME` | `ai-tutor-assets` | R2 bucket name |
| `R2_PUBLIC_URL` | Your R2 public URL | For serving audio files |

### Debug
| Variable | Value | Description |
|----------|-------|-------------|
| `DEBUG` | `false` | Set to false in production |

## Setup Instructions

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your web service
3. Go to **Environment** tab
4. Add each variable from the table above
5. Save and trigger a redeploy

## Testing AI Integration

After setting `MINIMAX_API_KEY`, the following features will work:

1. **AI Content Generation**: Personalized interview questions based on child's profile
2. **Prompt Templates**: 5 interview topics (self-introduction, interests, family, observation, scenarios)
3. **Mock Data Fallback**: If API fails, mock data will be used (with warning in logs)

Check application logs on Render to verify API calls:
```
📡 Calling MiniMax API: https://api.minimax.chat/v1/text/chatcompletion_v2
✅ MiniMax API success
```
