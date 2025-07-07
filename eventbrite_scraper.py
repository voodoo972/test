import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class EventbriteScraper:
    """Scraper for Eventbrite free events in Amsterdam"""
    
    def __init__(self):
        self.base_url = "https://www.eventbrite.com"
        self.search_url = "https://www.eventbrite.com/d/netherlands--amsterdam/free--events/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_events(self, max_events: int = 50) -> List[Dict]:
        """
        Scrape free events from Eventbrite Amsterdam
        
        Args:
            max_events: Maximum number of events to scrape
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            # Get the search results page
            response = self.session.get(self.search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event cards - Eventbrite typically uses specific class names
            event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event-card|search-event-card|event-item', re.I))
            
            # Also try generic containers that might contain events
            if not event_containers:
                event_containers = soup.find_all(['div'], attrs={'data-testid': re.compile(r'event', re.I)})
            
            # Fallback to any container with event-related attributes
            if not event_containers:
                event_containers = soup.find_all(['div', 'article'], attrs={'href': re.compile(r'/e/', re.I)})
            
            logger.info(f"Found {len(event_containers)} potential event containers on Eventbrite")
            
            for container in event_containers[:max_events]:
                event = self._extract_event_data(container)
                if event:
                    events.append(event)
            
            # Try to extract from JSON-LD structured data if available
            json_events = self._extract_from_json_ld(soup)
            events.extend(json_events[:max_events - len(events)])
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite events: {str(e)}")
        
        return events[:max_events]
    
    def _extract_event_data(self, container) -> Optional[Dict]:
        """Extract event data from a container element"""
        try:
            event = {
                'source': 'Eventbrite',
                'cost': 'Free',
                'category': 'Community',  # Default category
                'image': 'https://via.placeholder.com/400x250'
            }
            
            # Extract title - try multiple selectors
            title_elem = (
                container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|name|heading', re.I)) or
                container.find(['a'], class_=re.compile(r'event-title|title', re.I)) or
                container.find(['a'], href=re.compile(r'/e/', re.I))
            )
            
            if title_elem:
                event['title'] = title_elem.get_text(strip=True)
            else:
                return None
            
            # Extract event URL for more details
            link_elem = container.find('a', href=re.compile(r'/e/', re.I))
            event_url = None
            if link_elem:
                event_url = link_elem.get('href')
                if event_url and not event_url.startswith('http'):
                    event_url = self.base_url + event_url
            
            # Extract date and time
            date_elem = (
                container.find(['time']) or
                container.find(['div', 'span'], class_=re.compile(r'date|time', re.I))
            )
            
            if date_elem:
                # Try to get datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    parsed_date = self._parse_datetime_attr(datetime_attr)
                    if parsed_date:
                        event['date'] = parsed_date['date']
                        event['time'] = parsed_date['time']
                else:
                    # Parse from text content
                    date_text = date_elem.get_text(strip=True)
                    parsed_date = self._parse_date_text(date_text)
                    if parsed_date:
                        event['date'] = parsed_date['date']
                        event['time'] = parsed_date['time']
            
            # Extract location
            location_elem = container.find(['div', 'span'], class_=re.compile(r'location|venue|address', re.I))
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                event['location'] = location_text
                if 'amsterdam' not in location_text.lower():
                    event['address'] = location_text + ', Amsterdam'
                else:
                    event['address'] = location_text
            else:
                event['location'] = 'Amsterdam'
                event['address'] = 'Amsterdam, Netherlands'
            
            # Extract description
            desc_elem = container.find(['p', 'div'], class_=re.compile(r'description|summary|excerpt', re.I))
            if desc_elem:
                event['description'] = desc_elem.get_text(strip=True)[:300] + '...'
            else:
                event['description'] = f"Join this free event in Amsterdam. Check {event['title']} for more details."
            
            # Extract image
            img_elem = container.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = self.base_url + img_src
                    event['image'] = img_src
            
            # Extract organizer
            organizer_elem = container.find(['div', 'span'], class_=re.compile(r'organizer|host|by', re.I))
            if organizer_elem:
                event['organizer'] = organizer_elem.get_text(strip=True)
            else:
                event['organizer'] = 'Eventbrite Organizer'
            
            # Determine category
            event['category'] = self._determine_category(event.get('title', ''), event.get('description', ''))
            
            # If we have an event URL, try to get more details
            if event_url:
                additional_data = self._scrape_event_details(event_url)
                if additional_data:
                    event.update(additional_data)
            
            return event
            
        except Exception as e:
            logger.error(f"Error extracting Eventbrite event data: {str(e)}")
            return None
    
    def _parse_datetime_attr(self, datetime_str: str) -> Optional[Dict]:
        """Parse datetime attribute"""
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return {
                'date': dt.strftime('%Y-%m-%d'),
                'time': dt.strftime('%H:%M')
            }
        except Exception:
            return None
    
    def _parse_date_text(self, date_text: str) -> Optional[Dict]:
        """Parse date from text content"""
        try:
            # Common patterns for Eventbrite
            patterns = [
                r'(\w+),\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Monday, July 15, 2025
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # July 15, 2025
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # 15 July 2025
            ]
            
            # Time patterns
            time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)?'
            
            time_str = "All day"
            time_match = re.search(time_pattern, date_text, re.I)
            if time_match:
                hour, minute, ampm = time_match.groups()
                if ampm:
                    time_str = f"{hour}:{minute} {ampm.upper()}"
                else:
                    time_str = f"{hour}:{minute}"
            
            # Try to extract date
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        if len(match.groups()) == 4:  # Has day name
                            day_name, month_name, day, year = match.groups()
                        else:  # No day name
                            month_name, day, year = match.groups()
                        
                        month_num = self._month_name_to_number(month_name)
                        date_obj = datetime(int(year), month_num, int(day))
                        
                        return {
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'time': time_str
                        }
                    except ValueError:
                        continue
            
            # Default to near future if parsing fails
            future_date = datetime.now() + timedelta(days=3)
            return {
                'date': future_date.strftime('%Y-%m-%d'),
                'time': time_str
            }
            
        except Exception as e:
            logger.error(f"Error parsing date text: {str(e)}")
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
    
    def _determine_category(self, title: str, description: str) -> str:
        """Determine event category based on title and description"""
        text = (title + ' ' + description).lower()
        
        categories = {
            'Music': ['music', 'concert', 'band', 'singer', 'dj', 'festival', 'jazz', 'classical', 'rock', 'pop', 'acoustic', 'live music'],
            'Art & Culture': ['art', 'exhibition', 'museum', 'gallery', 'culture', 'painting', 'sculpture', 'theater', 'theatre', 'cultural'],
            'Sports & Fitness': ['sport', 'fitness', 'yoga', 'running', 'cycling', 'football', 'basketball', 'workout', 'exercise', 'training'],
            'Community': ['community', 'meetup', 'networking', 'social', 'volunteer', 'charity', 'local', 'neighborhood'],
            'Entertainment': ['comedy', 'show', 'performance', 'entertainment', 'fun', 'party', 'celebration', 'karaoke', 'game'],
            'Wellness': ['wellness', 'meditation', 'mindfulness', 'health', 'therapy', 'healing', 'spiritual', 'mental health']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'Community'  # Default category for Eventbrite
    
    def _extract_from_json_ld(self, soup) -> List[Dict]:
        """Extract events from JSON-LD structured data"""
        events = []
        
        try:
            # Look for JSON-LD script tags
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle both single events and arrays
                    if isinstance(data, list):
                        items = data
                    else:
                        items = [data]
                    
                    for item in items:
                        if item.get('@type') == 'Event':
                            event = self._parse_json_ld_event(item)
                            if event:
                                events.append(event)
                                
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting JSON-LD events: {str(e)}")
        
        return events
    
    def _parse_json_ld_event(self, data: Dict) -> Optional[Dict]:
        """Parse event from JSON-LD data"""
        try:
            event = {
                'source': 'Eventbrite',
                'cost': 'Free',
                'category': 'Community'
            }
            
            # Extract basic info
            event['title'] = data.get('name', '')
            event['description'] = data.get('description', '')[:300] + '...'
            
            # Extract date/time
            start_date = data.get('startDate')
            if start_date:
                try:
                    dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    event['date'] = dt.strftime('%Y-%m-%d')
                    event['time'] = dt.strftime('%H:%M')
                except:
                    pass
            
            # Extract location
            location = data.get('location', {})
            if isinstance(location, dict):
                name = location.get('name', '')
                address = location.get('address', {})
                if isinstance(address, dict):
                    street = address.get('streetAddress', '')
                    city = address.get('addressLocality', 'Amsterdam')
                    event['location'] = name or street or 'Amsterdam'
                    event['address'] = f"{street}, {city}" if street else city
                else:
                    event['location'] = name or 'Amsterdam'
                    event['address'] = 'Amsterdam, Netherlands'
            
            # Extract organizer
            organizer = data.get('organizer', {})
            if isinstance(organizer, dict):
                event['organizer'] = organizer.get('name', 'Eventbrite Organizer')
            
            # Extract image
            image = data.get('image')
            if image:
                if isinstance(image, list):
                    image = image[0]
                if isinstance(image, dict):
                    event['image'] = image.get('url', 'https://via.placeholder.com/400x250')
                else:
                    event['image'] = str(image)
            
            # Determine category
            event['category'] = self._determine_category(event.get('title', ''), event.get('description', ''))
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing JSON-LD event: {str(e)}")
            return None
    
    def _scrape_event_details(self, event_url: str) -> Optional[Dict]:
        """Scrape additional details from individual event page"""
        try:
            response = self.session.get(event_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            additional_data = {}
            
            # Try to get better description
            desc_elem = soup.find(['div'], class_=re.compile(r'description|about|summary', re.I))
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 50:  # Only use if substantial
                    additional_data['description'] = desc_text[:300] + '...'
            
            # Try to get better location info
            location_elem = soup.find(['div', 'span'], class_=re.compile(r'venue|location|address', re.I))
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                if location_text and len(location_text) > 5:
                    additional_data['location'] = location_text
                    if 'amsterdam' not in location_text.lower():
                        additional_data['address'] = location_text + ', Amsterdam'
                    else:
                        additional_data['address'] = location_text
            
            return additional_data
            
        except Exception as e:
            logger.error(f"Error scraping event details from {event_url}: {str(e)}")
            return None

