"""
Flask REST API - Phase 4 Integration
Combines Phases 1-3 with Phase 4 features: Email, Webhooks, Analytics, Dashboard
"""

import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

import flask
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS

# Phase 1-3 imports (unchanged from Phase 3)
from local_engine import generate_site_local
from design_engine import DesignAnalyzer
from seo_engine import optimize_html_seo, analyze_seo_score, generate_sitemap_xml
from component_exporter import ComponentExporter
from content_library import ContentLibrary
from db_models import init_db, get_session, User, Site, ContentItem, EmailTemplate
from cms_backend import CMSBackend, get_cms

# Phase 4 imports
from email_sender import EmailSender, EmailMessage, EmailProvider
from email_service import EmailService, get_email_service, set_email_service
from webhooks import WebhookManager, WebhookEvent, get_webhook_manager, set_webhook_manager
from advanced_analytics import AnalyticsManager, AnalyticsEvent, get_analytics_manager, set_analytics_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///promptrix.db')
app.config['JSON_SORT_KEYS'] = False

# Initialize services
init_db(app)
set_email_service(EmailService.from_env())
set_webhook_manager(WebhookManager(db_path=os.getenv('WEBHOOKS_DB', 'webhooks.db')))
set_analytics_manager(AnalyticsManager(db_path=os.getenv('ANALYTICS_DB', 'analytics.db')))

cms = get_cms()
content_lib = ContentLibrary()

# ==================== MIDDLEWARE ====================

def require_auth(f):
    """Require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not api_key or api_key != os.getenv('API_KEY', 'dev-api-key'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def track_analytics(event_type, properties=None):
    """Track analytics event"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            visitor_id = request.args.get('visitor_id', 'anonymous')
            session_id = request.args.get('session_id', 'session')
            
            event = AnalyticsEvent(
                event_type=event_type,
                site_id=request.args.get('site_id', 'unknown'),
                visitor_id=visitor_id,
                session_id=session_id,
                properties=properties or {}
            )
            get_analytics_manager().track_event(event)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== PHASE 4: EMAIL ENDPOINTS ====================

@app.route('/api/email/send', methods=['POST'])
@require_auth
def send_email():
    """Send single email"""
    try:
        data = request.json
        service = get_email_service()
        
        result = service.send(
            to=data.get('to'),
            subject=data.get('subject'),
            html_content=data.get('html_content'),
            plain_text=data.get('plain_text')
        )
        
        # Dispatch webhook event
        get_webhook_manager().dispatch_event('email.sent', {
            'to': data.get('to'),
            'subject': data.get('subject'),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/email/send-batch', methods=['POST'])
@require_auth
def send_email_batch():
    """Send batch emails"""
    try:
        data = request.json
        service = get_email_service()
        
        results = service.send_batch(
            recipients=data.get('recipients', []),
            subject=data.get('subject'),
            html_content=data.get('html_content'),
            plain_text=data.get('plain_text')
        )
        
        return jsonify({
            'total': len(results),
            'sent': sum(1 for r in results if r.get('success')),
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"Batch email send failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/email/send-template', methods=['POST'])
@require_auth
def send_email_template():
    """Send email from template"""
    try:
        data = request.json
        service = get_email_service()
        
        result = service.send_from_template(
            to=data.get('to'),
            template_type=data.get('template_type'),
            variables=data.get('variables', {})
        )
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Template email send failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/email/status/<email_id>', methods=['GET'])
@require_auth
def email_status(email_id):
    """Get email delivery status"""
    try:
        service = get_email_service()
        status = service.get_status(email_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/email/logs', methods=['GET'])
@require_auth
def email_logs():
    """Get email delivery logs"""
    try:
        service = get_email_service()
        limit = request.args.get('limit', 100, type=int)
        logs = service.get_logs(limit=limit)
        return jsonify({'logs': logs}), 200
    except Exception as e:
        logger.error(f"Logs retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/email/process-queue', methods=['POST'])
@require_auth
def process_email_queue():
    """Process pending emails"""
    try:
        service = get_email_service()
        stats = service.process_queue(batch_size=request.json.get('batch_size', 10))
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Queue processing failed: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== PHASE 4: WEBHOOK ENDPOINTS ====================

@app.route('/api/webhooks', methods=['POST'])
@require_auth
def create_webhook():
    """Create webhook"""
    try:
        data = request.json
        manager = get_webhook_manager()
        
        result = manager.create_webhook(
            user_id=data.get('user_id'),
            url=data.get('url'),
            events=data.get('events', [])
        )
        
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Webhook creation failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/<webhook_id>', methods=['GET'])
@require_auth
def get_webhook(webhook_id):
    """Get webhook"""
    try:
        manager = get_webhook_manager()
        webhook = manager.get_webhook(webhook_id)
        
        if not webhook:
            return jsonify({'error': 'Not found'}), 404
        
        return jsonify(webhook.to_dict()), 200
    except Exception as e:
        logger.error(f"Webhook retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/user/<user_id>', methods=['GET'])
@require_auth
def user_webhooks(user_id):
    """Get user webhooks"""
    try:
        manager = get_webhook_manager()
        webhooks = manager.get_user_webhooks(user_id)
        
        return jsonify({
            'webhooks': [w.to_dict() for w in webhooks]
        }), 200
    except Exception as e:
        logger.error(f"User webhooks retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/<webhook_id>', methods=['PUT'])
@require_auth
def update_webhook(webhook_id):
    """Update webhook"""
    try:
        data = request.json
        manager = get_webhook_manager()
        
        success = manager.update_webhook(webhook_id, **data)
        
        if not success:
            return jsonify({'error': 'Update failed'}), 400
        
        webhook = manager.get_webhook(webhook_id)
        return jsonify(webhook.to_dict()), 200
    except Exception as e:
        logger.error(f"Webhook update failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/<webhook_id>', methods=['DELETE'])
@require_auth
def delete_webhook(webhook_id):
    """Delete webhook"""
    try:
        manager = get_webhook_manager()
        success = manager.delete_webhook(webhook_id)
        
        if not success:
            return jsonify({'error': 'Delete failed'}), 400
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Webhook deletion failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/logs/<webhook_id>', methods=['GET'])
@require_auth
def webhook_logs(webhook_id):
    """Get webhook delivery logs"""
    try:
        manager = get_webhook_manager()
        limit = request.args.get('limit', 100, type=int)
        logs = manager.get_delivery_logs(webhook_id, limit=limit)
        
        return jsonify({'logs': logs}), 200
    except Exception as e:
        logger.error(f"Webhook logs retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks/process', methods=['POST'])
@require_auth
def process_webhooks():
    """Process pending webhook deliveries"""
    try:
        manager = get_webhook_manager()
        batch_size = request.json.get('batch_size', 10) if request.json else 10
        stats = manager.process_deliveries(batch_size=batch_size)
        
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== PHASE 4: ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/track', methods=['POST'])
def track_event():
    """Track analytics event"""
    try:
        data = request.json
        manager = get_analytics_manager()
        
        event = AnalyticsEvent(
            event_type=data.get('type'),
            site_id=data.get('site_id'),
            visitor_id=data.get('visitor_id'),
            session_id=data.get('session_id'),
            properties=data.get('properties', {})
        )
        
        success = manager.track_event(event)
        
        return jsonify({
            'event_id': event.id,
            'tracked': success
        }), 200
    except Exception as e:
        logger.error(f"Event tracking failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics/conversion', methods=['POST'])
@require_auth
def track_conversion():
    """Track conversion"""
    try:
        data = request.json
        manager = get_analytics_manager()
        
        success = manager.track_conversion(
            site_id=data.get('site_id'),
            visitor_id=data.get('visitor_id'),
            conversion_type=data.get('type'),
            value=data.get('value', 1.0),
            properties=data.get('properties', {})
        )
        
        return jsonify({'tracked': success}), 200
    except Exception as e:
        logger.error(f"Conversion tracking failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics/summary/<site_id>', methods=['GET'])
def analytics_summary(site_id):
    """Get analytics summary"""
    try:
        manager = get_analytics_manager()
        days = request.args.get('days', 30, type=int)
        summary = manager.get_summary(site_id, days=days)
        
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Summary retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics/funnel/<site_id>', methods=['GET'])
def analytics_funnel(site_id):
    """Get conversion funnel"""
    try:
        manager = get_analytics_manager()
        events = request.args.getlist('events')
        days = request.args.get('days', 30, type=int)
        
        if not events:
            return jsonify({'error': 'No events specified'}), 400
        
        funnel = manager.get_funnel(site_id, event_sequence=events, days=days)
        
        return jsonify(funnel), 200
    except Exception as e:
        logger.error(f"Funnel retrieval failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics/cohorts/<site_id>', methods=['GET'])
def analytics_cohorts(site_id):
    """Get cohort analysis"""
    try:
        manager = get_analytics_manager()
        cohort_size = request.args.get('cohort_size', 7, type=int)
        analysis = manager.get_cohort_analysis(site_id, cohort_size_days=cohort_size)
        
        return jsonify(analysis), 200
    except Exception as e:
        logger.error(f"Cohort analysis failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics/events/<site_id>', methods=['GET'])
def analytics_events(site_id):
    """Get events report"""
    try:
        manager = get_analytics_manager()
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 100, type=int)
        report = manager.get_events_report(site_id, days=days, limit=limit)
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Events report failed: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Admin dashboard"""
    try:
        with open('dashboard.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Dashboard not found'}), 404


@app.route('/dashboard/api/stats', methods=['GET'])
@require_auth
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        manager = get_analytics_manager()
        
        # Get summary for default site
        summary = manager.get_summary('default', days=30)
        
        return jsonify({
            'analytics': summary['metrics'],
            'updated_at': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Dashboard stats failed: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== PHASE 3 ENDPOINTS (MAINTAINED) ====================

@app.route('/api/generate/site', methods=['POST'])
@track_analytics('site_generated')
def generate_site():
    """Generate HTML site"""
    try:
        data = request.json
        config = data.get('config', {})
        site_type = config.get('type', 'blog')
        
        html = generate_site_local(config)
        
        # Dispatch webhook
        get_webhook_manager().dispatch_event('site.created', {
            'site_type': site_type,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'html': html,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Site generation failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/design/analyze', methods=['POST'])
def analyze_design():
    """Analyze design"""
    try:
        data = request.json
        html = data.get('html', '')
        
        analyzer = DesignAnalyzer()
        analysis = analyzer.analyze_design(html)
        
        return jsonify(analysis), 200
    except Exception as e:
        logger.error(f"Design analysis failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/seo/optimize', methods=['POST'])
def optimize_seo():
    """Optimize HTML for SEO"""
    try:
        data = request.json
        html = data.get('html', '')
        
        optimized = optimize_html_seo(html, data.get('meta', {}))
        score = analyze_seo_score(html)
        
        return jsonify({
            'html': optimized,
            'score': score
        }), 200
    except Exception as e:
        logger.error(f"SEO optimization failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/export/react', methods=['POST'])
def export_react():
    """Export to React"""
    try:
        data = request.json
        html = data.get('html', '')
        
        exporter = ComponentExporter()
        react_code = exporter.export_as_react(html)
        
        return jsonify({
            'code': react_code,
            'format': 'jsx'
        }), 200
    except Exception as e:
        logger.error(f"React export failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/content/search', methods=['GET'])
def search_content():
    """Search content library"""
    try:
        query = request.args.get('q', '')
        site_type = request.args.get('type', 'blog')
        
        results = content_lib.search_content(query, site_type)
        
        return jsonify({
            'query': query,
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"Content search failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/cms/sites', methods=['GET', 'POST'])
@require_auth
def cms_sites():
    """CMS: Get or create sites"""
    try:
        if request.method == 'GET':
            sites = cms.list_sites()
            return jsonify({'sites': sites}), 200
        else:
            data = request.json
            site = cms.create_site(data)
            return jsonify(site), 201
    except Exception as e:
        logger.error(f"CMS sites operation failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/cms/sites/<site_id>', methods=['GET', 'PUT', 'DELETE'])
@require_auth
def cms_site(site_id):
    """CMS: Get, update, or delete site"""
    try:
        if request.method == 'GET':
            site = cms.get_site(site_id)
            return jsonify(site), 200
        elif request.method == 'PUT':
            data = request.json
            site = cms.update_site(site_id, data)
            return jsonify(site), 200
        else:
            cms.delete_site(site_id)
            return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"CMS site operation failed: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== HEALTH & INFO ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': '4.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/info', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        'name': 'Promptrix Phase 4',
        'version': '4.0.0',
        'description': 'Complete website generation platform with email, webhooks, and analytics',
        'features': {
            'phase1': 'HTML generation, design analysis, SEO optimization',
            'phase2': 'CMS, content library, email templates',
            'phase3': 'REST API with 25+ endpoints',
            'phase4': 'Email service, webhooks, advanced analytics, admin dashboard'
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500"""
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== STARTUP ====================

if __name__ == '__main__':
    # Create required databases
    os.makedirs('data', exist_ok=True)
    
    # Initialize
    with app.app_context():
        init_db(app)
    
    # Run server
    debug = os.getenv('DEBUG', 'False') == 'True'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Promptrix Phase 4 API on {host}:{port}")
    logger.info("Features: Site Generation, Design Analysis, SEO Optimization, CMS, Email, Webhooks, Analytics")
    
    app.run(host=host, port=port, debug=debug)
