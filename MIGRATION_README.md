# Tennis Database Migration to Render

## 🚀 Quick Start

### Prerequisites
1. **Render PostgreSQL Database**: Create a free PostgreSQL database on [Render](https://dashboard.render.com)
2. **Environment Variables**: Set up your `DATABASE_URL` in `.env` file
3. **Python Dependencies**: Install required packages

### Setup
```bash
# Install dependencies
pip install pandas sqlalchemy psycopg2-binary python-dotenv

# Set up environment variables
echo "DATABASE_URL=postgresql://user:pass@host:port/db" > .env

# Run migration
python migrate_to_render.py
```

## 📊 What Gets Migrated

### Essential Data Only (Free Tier Optimized):
- **Matches**: 100,000 recent matches (2000+)
- **Players**: 5,000 top players
- **Rankings**: 50,000 recent rankings (2020+)

### Data Filters:
- ✅ **Recent matches**: 2000+ only
- ✅ **Top players**: Most active players
- ✅ **Recent rankings**: 2020+ rankings
- ✅ **Optimized size**: Fits free tier storage

## 🔧 Configuration

### Environment Variables:
```bash
DATABASE_URL=postgresql://username:password@hostname:port/database
```

### Custom Filters (Optional):
Edit `migrate_to_render.py` to adjust data selection:
```python
essential_tables = {
    'matches': "SELECT * FROM matches WHERE event_year >= 2000 LIMIT 100000",
    'players': "SELECT * FROM players LIMIT 5000", 
    'rankings': "SELECT * FROM rankings WHERE ranking_date >= '2020-01-01' LIMIT 50000"
}
```

## 📈 Expected Results

- **Migration Time**: 2-5 minutes
- **Database Size**: ~50-100MB (fits free tier)
- **Records**: ~155,000 total records
- **Tables**: 3 essential tables

## 🚀 Deployment

After successful migration:
1. Update your Streamlit app to use `DATABASE_URL`
2. Deploy to Render with the same environment variable
3. Your tennis database will be ready for queries!

## 🔍 Troubleshooting

### Common Issues:
- **Storage Full**: Use selective migration (already optimized)
- **Connection Failed**: Check `DATABASE_URL` format
- **SSL Errors**: Ensure `sslmode=require` in connection string

### Support:
- Check Render database logs
- Verify environment variables
- Test connection with `python test_db_connection.py`
