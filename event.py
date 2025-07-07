from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from typing import Dict, List, Optional

db = SQLAlchemy()

class Event(db.Model):
    """Event model for storing scraped events"""
    
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.String(20))  # YYYY-MM-DD format
    time = db.Column(db.String(50))  # Time string like "19:00 - 21:00"
    location = db.Column(db.String(255))
    address = db.Column(db.String(255))
    category = db.Column(db.String(100))
    cost = db.Column(db.String(50))
    organizer = db.Column(db.String(255))
    source = db.Column(db.String(100))  # 'I amsterdam', 'Eventbrite', etc.
    image = db.Column(db.String(500))
    source_url = db.Column(db.String(500))  # Original URL from source
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('title', 'date', 'source', name='unique_event'),
    )
    
    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'address': self.address,
            'category': self.category,
            'cost': self.cost,
            'organizer': self.organizer,
            'source': self.source,
            'image': self.image,
            'source_url': self.source_url
        }
    
    @classmethod
    def create_from_scraped_data(cls, data: Dict) -> 'Event':
        """Create Event instance from scraped data"""
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            date=data.get('date', ''),
            time=data.get('time', ''),
            location=data.get('location', ''),
            address=data.get('address', ''),
            category=data.get('category', ''),
            cost=data.get('cost', 'Free'),
            organizer=data.get('organizer', ''),
            source=data.get('source', ''),
            image=data.get('image', ''),
            source_url=data.get('source_url', '')
        )
    
    @classmethod
    def get_active_events(cls, 
                         search: Optional[str] = None,
                         category: Optional[str] = None,
                         date_filter: Optional[str] = None) -> List['Event']:
        """Get active events with optional filtering"""
        query = cls.query.filter(cls.is_active == True)
        
        # Apply search filter
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                db.or_(
                    cls.title.ilike(search_term),
                    cls.description.ilike(search_term),
                    cls.location.ilike(search_term)
                )
            )
        
        # Apply category filter
        if category and category != 'All':
            query = query.filter(cls.category == category)
        
        # Apply date filter
        if date_filter:
            today = datetime.now().date()
            
            if date_filter == 'today':
                query = query.filter(cls.date == today.strftime('%Y-%m-%d'))
            elif date_filter == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                query = query.filter(cls.date == tomorrow.strftime('%Y-%m-%d'))
            elif date_filter == 'this-week':
                week_from_now = today + timedelta(days=7)
                query = query.filter(
                    cls.date >= today.strftime('%Y-%m-%d'),
                    cls.date <= week_from_now.strftime('%Y-%m-%d')
                )
            elif date_filter == 'this-weekend':
                # Find next Saturday and Sunday
                days_until_saturday = (5 - today.weekday()) % 7
                if days_until_saturday == 0 and today.weekday() == 5:  # Today is Saturday
                    saturday = today
                else:
                    saturday = today + timedelta(days=days_until_saturday)
                sunday = saturday + timedelta(days=1)
                
                query = query.filter(
                    db.or_(
                        cls.date == saturday.strftime('%Y-%m-%d'),
                        cls.date == sunday.strftime('%Y-%m-%d')
                    )
                )
        
        # Order by date, then by time
        return query.order_by(cls.date.asc(), cls.time.asc()).all()
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique categories"""
        categories = db.session.query(cls.category).filter(
            cls.is_active == True,
            cls.category.isnot(None)
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        category_list.sort()
        category_list.insert(0, 'All')
        return category_list
    
    @classmethod
    def upsert_event(cls, data: Dict) -> 'Event':
        """Insert or update an event based on unique constraint"""
        try:
            # Try to find existing event
            existing = cls.query.filter(
                cls.title == data.get('title'),
                cls.date == data.get('date'),
                cls.source == data.get('source')
            ).first()
            
            if existing:
                # Update existing event
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                existing.is_active = True
                return existing
            else:
                # Create new event
                new_event = cls.create_from_scraped_data(data)
                db.session.add(new_event)
                return new_event
                
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def deactivate_old_events(cls, source: str, current_event_ids: List[int]):
        """Deactivate events from a source that are no longer found"""
        cls.query.filter(
            cls.source == source,
            cls.is_active == True,
            ~cls.id.in_(current_event_ids)
        ).update({'is_active': False}, synchronize_session=False)
    
    @classmethod
    def cleanup_old_events(cls, days_old: int = 30):
        """Remove events older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cls.query.filter(cls.created_at < cutoff_date).delete()
        db.session.commit()

