import { MapPin, Calendar, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-600 rounded-lg">
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Amsterdam Events
              </h1>
              <div className="flex items-center gap-1 text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span className="text-sm">Free & Low-Cost Activities</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <Heart className="h-4 w-4 mr-2" />
              Support Us
            </Button>
          </div>
        </div>
        
        <div className="mt-4">
          <p className="text-muted-foreground max-w-2xl">
            Discover amazing free and low-cost events happening in Amsterdam. 
            From art exhibitions to community gatherings, find your next adventure without breaking the bank.
          </p>
        </div>
      </div>
    </header>
  );
}

