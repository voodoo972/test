import logging
from typing import Dict, List
from datetime import datetime
from src.models.event import Event, db
from src.scrapers.iamsterdam_scraper import IAmsterdamScraper
from src.scrapers.eventbrite_scraper import EventbriteScraper

logger = logging.getLogger(__name__)

class DataManager:
    """Manages data scraping and database updates"""
    
    def __init__(self):
        self.iamsterdam_scraper = IAmsterdamScraper()
        self.eventbrite_scraper = EventbriteScraper()
    
    def update_all_events(self) -> Dict:
        """Update events from all sources"""
        logger.info("Starting event update process")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'sources': {},
            'total_events': 0,
            'errors': []
        }
        
        # Update from I amsterdam
        try:
            iamsterdam_result = self.update_iamsterdam_events()
            results['sources']['iamsterdam'] = iamsterdam_result
            results['total_events'] += iamsterdam_result.get('events_processed', 0)
        except Exception as e:
            error_msg = f"Error updating I amsterdam events: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['sources']['iamsterdam'] = {'error': error_msg}
        
        # Update from Eventbrite
        try:
            eventbrite_result = self.update_eventbrite_events()
            results['sources']['eventbrite'] = eventbrite_result
            results['total_events'] += eventbrite_result.get('events_processed', 0)
        except Exception as e:
            error_msg = f"Error updating Eventbrite events: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['sources']['eventbrite'] = {'error': error_msg}
        
        # Cleanup old events
        try:
            self.cleanup_old_events()
            results['cleanup'] = 'completed'
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['cleanup'] = error_msg
        
        logger.info(f"Event update completed. Total events: {results['total_events']}")
        return results
    
    def update_iamsterdam_events(self) -> Dict:
        """Update events from I amsterdam"""
        logger.info("Scraping events from I amsterdam")
        
        try:
            # Scrape events
            scraped_events = self.iamsterdam_scraper.scrape_events(max_events=25)
            
            # Process and save events
            processed_events = []
            current_event_ids = []
            
            for event_data in scraped_events:
                try:
                    # Validate required fields
                    if not event_data.get('title') or not event_data.get('date'):
                        logger.warning(f"Skipping event with missing required fields: {event_data}")
                        continue
                    
                    # Upsert event
                    event = Event.upsert_event(event_data)
                    db.session.commit()
                    
                    processed_events.append(event.to_dict())
                    current_event_ids.append(event.id)
                    
                except Exception as e:
                    logger.error(f"Error processing I amsterdam event: {str(e)}")
                    db.session.rollback()
                    continue
            
            # Deactivate events no longer found
            Event.deactivate_old_events('I amsterdam', current_event_ids)
            db.session.commit()
            
            result = {
                'events_scraped': len(scraped_events),
                'events_processed': len(processed_events),
                'events_deactivated': Event.query.filter(
                    Event.source == 'I amsterdam',
                    Event.is_active == False
                ).count(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            logger.info(f"I amsterdam update completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating I amsterdam events: {str(e)}")
            raise
    
    def update_eventbrite_events(self) -> Dict:
        """Update events from Eventbrite"""
        logger.info("Scraping events from Eventbrite")
        
        try:
            # Scrape events
            scraped_events = self.eventbrite_scraper.scrape_events(max_events=25)
            
            # Process and save events
            processed_events = []
            current_event_ids = []
            
            for event_data in scraped_events:
                try:
                    # Validate required fields
                    if not event_data.get('title') or not event_data.get('date'):
                        logger.warning(f"Skipping event with missing required fields: {event_data}")
                        continue
                    
                    # Upsert event
                    event = Event.upsert_event(event_data)
                    db.session.commit()
                    
                    processed_events.append(event.to_dict())
                    current_event_ids.append(event.id)
                    
                except Exception as e:
                    logger.error(f"Error processing Eventbrite event: {str(e)}")
                    db.session.rollback()
                    continue
            
            # Deactivate events no longer found
            Event.deactivate_old_events('Eventbrite', current_event_ids)
            db.session.commit()
            
            result = {
                'events_scraped': len(scraped_events),
                'events_processed': len(processed_events),
                'events_deactivated': Event.query.filter(
                    Event.source == 'Eventbrite',
                    Event.is_active == False
                ).count(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Eventbrite update completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating Eventbrite events: {str(e)}")
            raise
    
    def cleanup_old_events(self):
        """Clean up old events"""
        logger.info("Cleaning up old events")
        
        try:
            # Remove events older than 30 days
            Event.cleanup_old_events(days_old=30)
            logger.info("Old events cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise
    
    def get_update_status(self) -> Dict:
        """Get current status of events in database"""
        try:
            total_events = Event.query.filter(Event.is_active == True).count()
            iamsterdam_events = Event.query.filter(
                Event.source == 'I amsterdam',
                Event.is_active == True
            ).count()
            eventbrite_events = Event.query.filter(
                Event.source == 'Eventbrite',
                Event.is_active == True
            ).count()
            
            # Get latest update times
            latest_iamsterdam = Event.query.filter(
                Event.source == 'I amsterdam',
                Event.is_active == True
            ).order_by(Event.updated_at.desc()).first()
            
            latest_eventbrite = Event.query.filter(
                Event.source == 'Eventbrite',
                Event.is_active == True
            ).order_by(Event.updated_at.desc()).first()
            
            return {
                'total_active_events': total_events,
                'iamsterdam_events': iamsterdam_events,
                'eventbrite_events': eventbrite_events,
                'last_iamsterdam_update': latest_iamsterdam.updated_at.isoformat() if latest_iamsterdam else None,
                'last_eventbrite_update': latest_eventbrite.updated_at.isoformat() if latest_eventbrite else None,
                'categories': Event.get_categories()
            }
            
        except Exception as e:
            logger.error(f"Error getting update status: {str(e)}")
            raise
    
    def seed_sample_data(self):
        """Seed database with sample data for testing"""
        logger.info("Seeding database with sample data")
        
        sample_events = [
            {
                'title': 'Free Exhibition: We are here - A shared past, Muslims tell',
                'description': 'An exhibition exploring the shared history and stories of Muslims in Amsterdam and the Netherlands.',
                'date': '2025-07-03',
                'time': '09:00 - 18:00',
                'location': 'Amsterdam Public Library (OBA)',
                'address': 'Oosterdok 143, Amsterdam',
                'category': 'Art & Culture',
                'cost': 'Free',
                'organizer': 'Amsterdam Public Library',
                'source': 'I amsterdam',
                'image': 'https://via.placeholder.com/400x250'
            },
            {
                'title': 'Rooftop Open Mic Night',
                'description': 'Join us for an evening of music, poetry, and creative expression on our beautiful rooftop terrace.',
                'date': '2025-07-11',
                'time': '18:00 - 22:00',
                'location': 'Zoku Amsterdam',
                'address': 'Weesperstraat 105, Amsterdam',
                'category': 'Music',
                'cost': 'Free',
                'organizer': 'Zoku Amsterdam',
                'source': 'Eventbrite',
                'image': 'https://via.placeholder.com/400x250'
            },
            {
                'title': 'Community Lunch',
                'description': 'A weekly community lunch where neighbors can meet, share a meal, and connect with each other.',
                'date': '2025-07-09',
                'time': '12:00 - 14:00',
                'location': 'Equals Clubhouse',
                'address': 'Nieuwezijds Voorburgwal 32, Amsterdam',
                'category': 'Community',
                'cost': 'Free',
                'organizer': 'Equals Clubhouse',
                'source': 'Eventbrite',
                'image': 'https://via.placeholder.com/400x250'
            }
        ]
        
        try:
            for event_data in sample_events:
                Event.upsert_event(event_data)
            
            db.session.commit()
            logger.info(f"Seeded {len(sample_events)} sample events")
            
        except Exception as e:
            logger.error(f"Error seeding sample data: {str(e)}")
            db.session.rollback()
            raise

