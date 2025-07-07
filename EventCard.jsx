import { Calendar, MapPin, Clock, Tag, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export function EventCard({ event }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <Card className="h-full flex flex-col hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="p-0">
        <div className="relative">
          <img 
            src={event.image} 
            alt={event.title}
            className="w-full h-48 object-cover rounded-t-lg"
          />
          <Badge 
            variant="secondary" 
            className="absolute top-2 right-2 bg-green-100 text-green-800 border-green-200"
          >
            {event.cost}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg leading-tight line-clamp-2">
              {event.title}
            </h3>
          </div>
          
          <div className="space-y-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 flex-shrink-0" />
              <span>{formatDate(event.date)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 flex-shrink-0" />
              <span>{event.time}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 flex-shrink-0" />
              <span className="line-clamp-1">{event.location}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Tag className="h-4 w-4 flex-shrink-0" />
              <Badge variant="outline" className="text-xs">
                {event.category}
              </Badge>
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground line-clamp-3">
            {event.description}
          </p>
        </div>
      </CardContent>
      
      <CardFooter className="p-4 pt-0">
        <Button variant="outline" className="w-full" size="sm">
          <ExternalLink className="h-4 w-4 mr-2" />
          View Details
        </Button>
      </CardFooter>
    </Card>
  );
}

