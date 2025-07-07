# Data Sources for Amsterdam Event Aggregator

Based on the research conducted, here are the primary data sources for free and low-cost events in Amsterdam:

## 1. I amsterdam (iamsterdam.com)
- **URL**: https://www.iamsterdam.com/en/whats-on/calendar
- **Features**: 
  - Official Amsterdam tourism website
  - Has a "Free activities" filter
  - Comprehensive event listings with categories
  - Event details include time, location, and cost information
  - Well-structured event cards with images
- **Data Structure**: Events displayed as cards with date, title, location, time, and cost indicators
- **Pros**: Official source, reliable, comprehensive
- **Cons**: May require web scraping

## 2. Eventbrite
- **URL**: https://www.eventbrite.com/d/netherlands--amsterdam/free--events/
- **Features**:
  - Large collection of free events
  - Good filtering options (date, category, language)
  - Event details include organizer, location, time
  - User-generated content
- **Data Structure**: Event listings with images, titles, dates, locations, and pricing
- **Pros**: Large volume of events, API potentially available
- **Cons**: Mix of quality, some events may be spam

## 3. Additional Sources Identified
- **Amsterdam.org**: Free events section
- **AllEvents.in**: Amsterdam free events
- **Amsterdam Sights**: Free events and attractions
- **Reddit r/Amsterdam**: Community-driven recommendations
- **Local venues**: Individual venue websites and social media

## 4. Event Categories Found
- Art exhibitions and galleries
- Music performances and concerts
- Community events and meetups
- Workshops and classes
- Outdoor activities and festivals
- Cultural events and celebrations
- Sports and fitness activities
- Networking events

## 5. Implementation Strategy
For the initial version, we will:
1. Create a simple frontend that displays sample events
2. Use static data initially to demonstrate the concept
3. Later implement web scraping or API integration for live data
4. Focus on the user experience and donation functionality

## 6. Sample Event Data Structure
Based on the research, events should include:
- Title
- Date and time
- Location (venue name and address)
- Description
- Category
- Cost (free/low-cost indicator)
- Image (if available)
- Source URL
- Organizer information

