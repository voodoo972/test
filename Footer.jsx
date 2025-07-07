import { Heart, Mail, Github, ExternalLink } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-gray-50 border-t mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About Section */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">About Amsterdam Events</h3>
            <p className="text-sm text-muted-foreground mb-4">
              We aggregate free and low-cost events from across Amsterdam to help you discover 
              amazing activities without spending a fortune. Built with love for the Amsterdam community.
            </p>
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <span>Made with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span>in Amsterdam</span>
            </div>
          </div>

          {/* Data Sources */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Data Sources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a 
                  href="https://www.iamsterdam.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-blue-600 flex items-center gap-1"
                >
                  I amsterdam
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a 
                  href="https://www.eventbrite.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-blue-600 flex items-center gap-1"
                >
                  Eventbrite
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <span className="text-muted-foreground">Local venues & organizers</span>
              </li>
              <li>
                <span className="text-muted-foreground">Community submissions</span>
              </li>
            </ul>
          </div>

          {/* Contact & Support */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Get Involved</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a 
                  href="mailto:hello@amsterdamevents.com" 
                  className="text-muted-foreground hover:text-blue-600 flex items-center gap-1"
                >
                  <Mail className="h-4 w-4" />
                  Submit an event
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  className="text-muted-foreground hover:text-blue-600 flex items-center gap-1"
                >
                  <Github className="h-4 w-4" />
                  Contribute on GitHub
                </a>
              </li>
              <li>
                <a 
                  href="#donation" 
                  className="text-muted-foreground hover:text-blue-600 flex items-center gap-1"
                >
                  <Heart className="h-4 w-4" />
                  Support the project
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t mt-8 pt-6 text-center">
          <p className="text-sm text-muted-foreground">
            © 2025 Amsterdam Events. This is a community project. Event information is aggregated from public sources.
          </p>
        </div>
      </div>
    </footer>
  );
}

