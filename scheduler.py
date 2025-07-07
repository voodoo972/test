import logging
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from src.scrapers.data_manager import DataManager

logger = logging.getLogger(__name__)

class EventScheduler:
    """Scheduler for automated event data updates"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.data_manager = None
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            daemon=True,
            timezone='Europe/Amsterdam'
        )
        
        # Initialize data manager
        with app.app_context():
            self.data_manager = DataManager()
        
        # Register shutdown handler
        atexit.register(lambda: self.shutdown())
    
    def start_scheduler(self, interval_minutes=20):
        """Start the scheduler with specified interval"""
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            # Add job for periodic updates
            self.scheduler.add_job(
                func=self.scheduled_update,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='event_update_job',
                name='Update Amsterdam Events',
                replace_existing=True,
                max_instances=1  # Prevent overlapping jobs
            )
            
            # Start the scheduler
            self.scheduler.start()
            
            logger.info(f"Event scheduler started with {interval_minutes} minute intervals")
            
            # Run initial update
            self.scheduler.add_job(
                func=self.scheduled_update,
                trigger='date',
                run_date=datetime.now(),
                id='initial_update',
                name='Initial Event Update'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            return False
    
    def scheduled_update(self):
        """Perform scheduled event update"""
        logger.info("Starting scheduled event update")
        
        try:
            with self.app.app_context():
                result = self.data_manager.update_all_events()
                
                logger.info(f"Scheduled update completed successfully: {result['total_events']} events processed")
                
                if result.get('errors'):
                    logger.warning(f"Update completed with errors: {result['errors']}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error during scheduled update: {str(e)}")
            raise
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Event scheduler stopped")
    
    def shutdown(self):
        """Shutdown handler"""
        self.stop_scheduler()
    
    def get_job_status(self):
        """Get status of scheduled jobs"""
        if not self.scheduler:
            return {'status': 'not_initialized'}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'status': 'running' if self.scheduler.running else 'stopped',
            'jobs': jobs
        }
    
    def trigger_manual_update(self):
        """Trigger a manual update immediately"""
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            # Add one-time job
            self.scheduler.add_job(
                func=self.scheduled_update,
                trigger='date',
                run_date=datetime.now(),
                id=f'manual_update_{datetime.now().timestamp()}',
                name='Manual Event Update'
            )
            
            logger.info("Manual update triggered")
            return True
            
        except Exception as e:
            logger.error(f"Error triggering manual update: {str(e)}")
            return False

# Global scheduler instance
event_scheduler = EventScheduler()

def init_scheduler(app, start_immediately=True, interval_minutes=20):
    """Initialize and start the event scheduler"""
    try:
        event_scheduler.init_app(app)
        
        if start_immediately:
            success = event_scheduler.start_scheduler(interval_minutes)
            if success:
                logger.info(f"Event scheduler initialized and started with {interval_minutes} minute intervals")
            else:
                logger.error("Failed to start event scheduler")
            return success
        else:
            logger.info("Event scheduler initialized but not started")
            return True
            
    except Exception as e:
        logger.error(f"Error initializing scheduler: {str(e)}")
        return False

