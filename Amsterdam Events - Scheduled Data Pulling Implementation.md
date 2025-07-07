# Amsterdam Events - Scheduled Data Pulling Implementation

## 🚀 Overview

Your Amsterdam Events application has been upgraded with **automated data pulling** that continuously scrapes and updates events from I amsterdam and Eventbrite every 15-30 minutes. This ensures your users always see the latest free and low-cost events in Amsterdam.

## ✨ New Features Added

### 1. **Automated Data Scraping**
- **I amsterdam Scraper**: Pulls free events from the official I amsterdam website
- **Eventbrite Scraper**: Extracts free events from Eventbrite Amsterdam
- **Smart Filtering**: Only includes free or low-cost events
- **Category Detection**: Automatically categorizes events (Art & Culture, Music, Community, etc.)

### 2. **Database Integration**
- **SQLite Database**: Persistent storage for all events
- **Event Deduplication**: Prevents duplicate events from the same source
- **Data Validation**: Ensures event quality and completeness
- **Automatic Cleanup**: Removes old events after 30 days

### 3. **Scheduled Updates**
- **20-Minute Intervals**: Automatic updates every 20 minutes (configurable)
- **Background Processing**: Non-blocking updates that don't affect user experience
- **Error Handling**: Robust error handling with logging
- **Manual Triggers**: API endpoints to manually trigger updates

### 4. **Enhanced API**
- **Real-time Data**: Events served from database with latest information
- **Status Monitoring**: Health checks and scheduler status endpoints
- **Manual Controls**: Trigger scraping and view update status

## 🛠 Technical Implementation

### Database Schema
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date VARCHAR(20),           -- YYYY-MM-DD format
    time VARCHAR(50),           -- "19:00 - 21:00" format
    location VARCHAR(255),
    address VARCHAR(255),
    category VARCHAR(100),
    cost VARCHAR(50),
    organizer VARCHAR(255),
    source VARCHAR(100),        -- 'I amsterdam', 'Eventbrite'
    image VARCHAR(500),
    source_url VARCHAR(500),
    created_at DATETIME,
    updated_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Scraping Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   Data Manager   │───▶│    Database     │
│ (20min intervals)│    │                  │    │   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │    Scrapers      │
                       │ ┌──────────────┐ │
                       │ │ I amsterdam  │ │
                       │ └──────────────┘ │
                       │ ┌──────────────┐ │
                       │ │ Eventbrite   │ │
                       │ └──────────────┘ │
                       └──────────────────┘
```

### New API Endpoints

#### Event Management
- `GET /api/events` - Get filtered events from database
- `GET /api/events/{id}` - Get specific event
- `GET /api/categories` - Get available categories
- `GET /api/health` - Health check with scheduler status

#### Scheduler Management
- `POST /api/scrape` - Manually trigger scraping
- `GET /api/scheduler/status` - Get scheduler and data status
- `POST /api/seed` - Seed sample data (testing)

#### Example API Response
```json
{
  "events": [
    {
      "id": 1,
      "title": "Free Concert in Vondelpark",
      "description": "Enjoy live music in Amsterdam's most famous park...",
      "date": "2025-07-15",
      "time": "19:00 - 21:00",
      "location": "Vondelpark",
      "address": "Vondelpark, Amsterdam",
      "category": "Music",
      "cost": "Free",
      "organizer": "Vondelpark Events",
      "source": "I amsterdam",
      "image": "https://example.com/image.jpg"
    }
  ],
  "total": 1
}
```

## 📊 Data Sources & Scraping Strategy

### I amsterdam (iamsterdam.com)
- **Target**: Free cultural events and exhibitions
- **Method**: HTML parsing with BeautifulSoup
- **Frequency**: Every 20 minutes
- **Categories**: Primarily Art & Culture, some Music and Community
- **Data Quality**: High (official tourism website)

### Eventbrite (eventbrite.com)
- **Target**: Free community events and meetups
- **Method**: HTML parsing + JSON-LD structured data
- **Frequency**: Every 20 minutes
- **Categories**: Community, Music, Wellness, Entertainment
- **Data Quality**: Variable (user-generated content)

### Scraping Features
- **Respectful Scraping**: Rate limiting and user-agent headers
- **Error Resilience**: Continues if one source fails
- **Data Validation**: Checks for required fields
- **Smart Categorization**: Keyword-based category detection
- **Image Handling**: Extracts and validates event images

## ⚙️ Configuration Options

### Scheduler Settings
```python
# In src/main.py
init_scheduler(app, start_immediately=True, interval_minutes=20)

# Available intervals:
# - 15 minutes: interval_minutes=15
# - 20 minutes: interval_minutes=20 (recommended)
# - 30 minutes: interval_minutes=30
# - 60 minutes: interval_minutes=60
```

### Scraping Limits
```python
# In scrapers
max_events_per_source = 25  # Configurable per scraper
cleanup_days = 30          # Remove events older than 30 days
```

## 🔧 Deployment & Setup

### Local Development
```bash
# Install dependencies
cd amsterdam-events-backend
source venv/bin/activate
pip install -r requirements.txt

# Run with scheduler
python src/main.py
```

### Production Deployment
The application is ready for deployment with:
- **APScheduler**: Background task scheduling
- **SQLite**: Lightweight database (upgradeable to PostgreSQL)
- **Logging**: Comprehensive logging for monitoring
- **Error Handling**: Graceful failure handling

### Environment Variables (Optional)
```bash
# Optional configuration
export SCRAPING_INTERVAL=20        # Minutes between updates
export MAX_EVENTS_PER_SOURCE=25    # Events to scrape per source
export LOG_LEVEL=INFO              # Logging level
```

## 📈 Monitoring & Maintenance

### Health Monitoring
```bash
# Check application health
curl https://your-domain.com/api/health

# Response includes:
{
  "status": "healthy",
  "active_events": 45,
  "scheduler": {
    "status": "running",
    "jobs": [...]
  }
}
```

### Manual Operations
```bash
# Trigger manual scraping
curl -X POST https://your-domain.com/api/scrape

# Check scheduler status
curl https://your-domain.com/api/scheduler/status

# Seed sample data (testing)
curl -X POST https://your-domain.com/api/seed
```

### Log Monitoring
```bash
# Key log messages to monitor:
# - "Event scheduler started with X minute intervals"
# - "Scheduled update completed successfully: X events processed"
# - "Error during scheduled update: ..."
# - "I amsterdam update completed: {...}"
# - "Eventbrite update completed: {...}"
```

## 🚨 Error Handling & Recovery

### Common Issues & Solutions

#### 1. **Scraping Failures**
- **Cause**: Website structure changes, network issues
- **Detection**: Error logs, reduced event count
- **Recovery**: Automatic retry, fallback to other sources
- **Action**: Monitor logs, update scrapers if needed

#### 2. **Database Issues**
- **Cause**: Disk space, corruption, locks
- **Detection**: Health check failures
- **Recovery**: Automatic reconnection, transaction rollback
- **Action**: Check disk space, restart if needed

#### 3. **Scheduler Problems**
- **Cause**: Memory issues, timezone problems
- **Detection**: No recent updates, health check
- **Recovery**: Automatic restart, manual trigger
- **Action**: Check system resources, restart application

### Maintenance Tasks

#### Weekly
- Check application logs for errors
- Verify event count and data quality
- Monitor scraping success rates

#### Monthly
- Review and update scraper selectors if needed
- Check database size and performance
- Update dependencies and security patches

#### Quarterly
- Analyze event categories and sources
- Optimize scraping intervals based on usage
- Consider adding new data sources

## 💡 Future Enhancements

### Short-term (1-3 months)
1. **Additional Sources**
   - Facebook Events (free events)
   - Meetup.com (community events)
   - Local venue websites

2. **Enhanced Filtering**
   - Location-based filtering (neighborhoods)
   - Time-based filtering (morning, evening)
   - Accessibility information

3. **Data Quality**
   - Event image optimization
   - Duplicate detection across sources
   - User feedback integration

### Medium-term (3-6 months)
1. **Real-time Updates**
   - WebSocket notifications for new events
   - Push notifications for mobile users
   - Email alerts for saved searches

2. **Advanced Features**
   - Event recommendations based on user preferences
   - Calendar integration (iCal export)
   - Social sharing optimization

3. **Analytics**
   - Event popularity tracking
   - User engagement metrics
   - Source performance analysis

### Long-term (6+ months)
1. **Machine Learning**
   - Intelligent event categorization
   - Personalized recommendations
   - Predictive event discovery

2. **Multi-city Expansion**
   - Rotterdam, The Hague, Utrecht
   - Scalable scraping architecture
   - City-specific customization

3. **Community Features**
   - User-submitted events
   - Event reviews and ratings
   - Community-driven curation

## 📊 Performance Metrics

### Expected Performance
- **Update Frequency**: Every 20 minutes
- **Events per Update**: 25-50 new/updated events
- **Database Size**: ~1000 active events (steady state)
- **API Response Time**: <200ms for event listings
- **Scraping Duration**: 30-60 seconds per source

### Success Metrics
- **Data Freshness**: 95% of events updated within 24 hours
- **Uptime**: 99.5% scheduler availability
- **Error Rate**: <5% scraping failures
- **Event Quality**: >90% events with complete information

## 🔐 Security & Compliance

### Data Protection
- **No Personal Data**: Only public event information
- **Rate Limiting**: Respectful scraping practices
- **Error Logging**: No sensitive data in logs
- **Database Security**: Local SQLite with file permissions

### Legal Compliance
- **Robots.txt**: Respect website scraping policies
- **Terms of Service**: Comply with source website terms
- **Attribution**: Credit original sources
- **Fair Use**: Non-commercial, educational purpose

### Best Practices
- **User-Agent**: Identify scraper appropriately
- **Request Delays**: Avoid overwhelming source servers
- **Error Handling**: Graceful failure without retries
- **Data Retention**: Automatic cleanup of old events

---

## 🎯 Quick Start Checklist

✅ **Application is running** with scheduled data pulling  
✅ **Database is initialized** and ready for events  
✅ **Scrapers are configured** for I amsterdam and Eventbrite  
✅ **Scheduler is active** with 20-minute intervals  
✅ **API endpoints** are available for monitoring  
✅ **Error handling** is implemented and logged  

### Next Steps:
1. **Deploy to production** (when ready)
2. **Monitor logs** for successful updates
3. **Test manual scraping** via API
4. **Verify event quality** and categories
5. **Set up monitoring** alerts
6. **Plan additional data sources**

Your Amsterdam Events application now automatically maintains fresh, up-to-date event listings without any manual intervention! 🎉

