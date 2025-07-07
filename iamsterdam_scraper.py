import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class IAmsterdamScraper:
    """Scraper for I amsterdam events website"""
    
    def __init__(self):
        self.base_url = "https://www.iamsterdam.com"
        self.events_url = "https://www.iamsterdam.com/en/whats-on/calendar"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_events(self, max_events: int = 50) -> List[Dict]:
        """
        Scrape events from I amsterdam website
        
        Args:
            max_events: Maximum number of events to scrape
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            # Get the main events page
            response = self.session.get(self.events_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event containers - these selectors may need adjustment based on actual site structure
            event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event|card|item', re.I))
            
            logger.info(f"Found {len(event_containers)} potential event containers")
            
            for container in event_containers[:max_events]:
                event = self._extract_event_data(container)
                if event and self._is_free_or_low_cost(event):
                    events.append(event)
            
            # Try to get more events from pagination or AJAX if available
            events.extend(self._scrape_additional_pages(max_events - len(events)))
            
        except Exception as e:
            logger.error(f"Error scraping I amsterdam events: {str(e)}")
        
        return events[:max_events]
    
    def _extract_event_data(self, container) -> Optional[Dict]:
        """Extract event data from a container element"""
        try:
            event = {
                'source': 'I amsterdam',
                'cost': 'Free',  # We're focusing on free events
                'category': 'Art & Culture',  # Default category
                'image': 'https://via.placeholder.com/400x250'
            }
            
            # Extract title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|heading|name', re.I))
            if not title_elem:
                title_elem = container.find(['a'], href=re.compile(r'/event|/whats-on', re.I))
            
            if title_elem:
                event['title'] = title_elem.get_text(strip=True)
            else:
                return None
            
            # Extract date and time
            date_elem = container.find(['time', 'div', 'span'], class_=re.compile(r'date|time', re.I))
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    event['date'] = parsed_date['date']
                    event['time'] = parsed_date['time']
            
            # Extract location
            location_elem = container.find(['div', 'span', 'p'], class_=re.compile(r'location|venue|address', re.I))
            if location_elem:
                event['location'] = location_elem.get_text(strip=True)
                event['address'] = event['location'] + ', Amsterdam'
            
            # Extract description
            desc_elem = container.find(['p', 'div'], class_=re.compile(r'description|summary|excerpt', re.I))
            if desc_elem:
                event['description'] = desc_elem.get_text(strip=True)[:300] + '...'
            
            # Extract image
            img_elem = container.find('img')
            if img_elem and img_elem.get('src'):
                img_src = img_elem.get('src')
                if img_src.startswith('/'):
                    img_src = self.base_url + img_src
                event['image'] = img_src
            
            # Extract organizer (try to find from various elements)
            organizer_elem = container.find(['div', 'span'], class_=re.compile(r'organizer|venue|host', re.I))
            if organizer_elem:
                event['organizer'] = organizer_elem.get_text(strip=True)
            else:
                event['organizer'] = 'I amsterdam'
            
            # Determine category based on title and description
            event['category'] = self._determine_category(event.get('title', ''), event.get('description', ''))
            
            return event
            
        except Exception as e:
            logger.error(f"Error extracting event data: {str(e)}")
            return None
    
    def _parse_date(self, date_text: str) -> Optional[Dict]:
        """Parse date text into structured format"""
        try:
            # Common date patterns
            patterns = [
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # 15 July 2025
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # July 15, 2025
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 15/07/2025
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2025-07-15
            ]
            
            # Time patterns
            time_pattern = r'(\d{1,2}):(\d{2})\s*(?:-\s*(\d{1,2}):(\d{2}))?'
            
            # Try to extract time
            time_match = re.search(time_pattern, date_text)
            time_str = "All day"
            if time_match:
                start_hour, start_min = time_match.groups()[:2]
                if time_match.groups()[2] and time_match.groups()[3]:
                    end_hour, end_min = time_match.groups()[2:4]
                    time_str = f"{start_hour}:{start_min} - {end_hour}:{end_min}"
                else:
                    time_str = f"{start_hour}:{start_min}"
            
            # Try to extract date
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    # Convert to standard format
                    today = datetime.now()
                    try:
                        if pattern == patterns[0]:  # 15 July 2025
                            day, month_name, year = match.groups()
                            month_num = self._month_name_to_number(month_name)
                            date_obj = datetime(int(year), month_num, int(day))
                        elif pattern == patterns[1]:  # July 15, 2025
                            month_name, day, year = match.groups()
                            month_num = self._month_name_to_number(month_name)
                            date_obj = datetime(int(year), month_num, int(day))
                        elif pattern == patterns[2]:  # 15/07/2025
                            day, month, year = match.groups()
                            date_obj = datetime(int(year), int(month), int(day))
                        elif pattern == patterns[3]:  # 2025-07-15
                            year, month, day = match.groups()
                            date_obj = datetime(int(year), int(month), int(day))
                        
                        return {
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'time': time_str
                        }
                    except ValueError:
                        continue
            
            # If no specific date found, assume it's upcoming
            future_date = datetime.now() + timedelta(days=7)
            return {
                'date': future_date.strftime('%Y-%m-%d'),
                'time': time_str
            }
            
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
            return None
    
    def _month_name_to_number(self, month_name: str) -> int:
        """Convert month name to number"""
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        return months.get(month_name.lower(), 1)
    
    def _is_free_or_low_cost(self, event: Dict) -> bool:
        """Check if event is free or low cost"""
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        
        free_keywords = ['free', 'gratis', 'no cost', 'complimentary', 'admission free']
        low_cost_keywords = ['€5', '€10', 'low cost', 'affordable', 'cheap']
        
        # Check for free keywords
        for keyword in free_keywords:
            if keyword in title or keyword in description:
                return True
        
        # Check for low cost keywords
        for keyword in low_cost_keywords:
            if keyword in title or keyword in description:
                return True
        
        # Default to including if no price information found
        return True
    
    def _determine_category(self, title: str, description: str) -> str:
        """Determine event category based on title and description"""
        text = (title + ' ' + description).lower()
        
        categories = {
            'Music': ['music', 'concert', 'band', 'singer', 'dj', 'festival', 'jazz', 'classical', 'rock', 'pop'],
            'Art & Culture': ['art', 'exhibition', 'museum', 'gallery', 'culture', 'painting', 'sculpture', 'theater', 'theatre'],
            'Sports & Fitness': ['sport', 'fitness', 'yoga', 'running', 'cycling', 'football', 'basketball', 'workout'],
            'Community': ['community', 'meetup', 'networking', 'social', 'volunteer', 'charity', 'local'],
            'Entertainment': ['comedy', 'show', 'performance', 'entertainment', 'fun', 'party', 'celebration'],
            'Wellness': ['wellness', 'meditation', 'mindfulness', 'health', 'therapy', 'healing', 'spiritual']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'Art & Culture'  # Default category
    
    def _scrape_additional_pages(self, remaining_events: int) -> List[Dict]:
        """Scrape additional pages if available"""
        # This would implement pagination scraping
        # For now, return empty list
        return []

