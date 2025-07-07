from flask import Blueprint, jsonify, request
from src.models.event import Event, db
from src.scheduler import event_scheduler
import logging

logger = logging.getLogger(__name__)

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '').lower()
        category = request.args.get('category', '')
        date_filter = request.args.get('date', '')
        
        # Get filtered events from database
        events = Event.get_active_events(
            search=search if search else None,
            category=category if category and category != 'All' else None,
            date_filter=date_filter if date_filter else None
        )
        
        # Convert to dictionaries
        events_data = [event.to_dict() for event in events]
        
        return jsonify({
            'events': events_data,
            'total': len(events_data)
        })
    
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    try:
        event = Event.query.filter(Event.id == event_id, Event.is_active == True).first()
        if event:
            return jsonify(event.to_dict())
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available event categories"""
    try:
        categories = Event.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        event_count = Event.query.filter(Event.is_active == True).count()
        
        # Check scheduler status
        scheduler_status = event_scheduler.get_job_status()
        
        return jsonify({
            'status': 'healthy', 
            'message': 'Amsterdam Events API is running',
            'active_events': event_count,
            'scheduler': scheduler_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 500

@events_bp.route('/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger event scraping"""
    try:
        # Trigger manual update through scheduler
        success = event_scheduler.trigger_manual_update()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Manual scraping triggered'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to trigger manual scraping'
            }), 500
    
    except Exception as e:
        logger.error(f"Error during manual scrape trigger: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status and job information"""
    try:
        status = event_scheduler.get_job_status()
        
        # Add data manager status
        from src.scrapers.data_manager import DataManager
        data_manager = DataManager()
        update_status = data_manager.get_update_status()
        
        return jsonify({
            'scheduler': status,
            'data': update_status
        })
    
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/seed', methods=['POST'])
def seed_sample_data():
    """Seed database with sample data (for testing)"""
    try:
        from src.scrapers.data_manager import DataManager
        
        data_manager = DataManager()
        data_manager.seed_sample_data()
        
        return jsonify({
            'status': 'success',
            'message': 'Sample data seeded successfully'
        })
    
    except Exception as e:
        logger.error(f"Error seeding sample data: {str(e)}")
        return jsonify({'error': str(e)}), 500

