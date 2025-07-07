import { useState, useMemo } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { EventCard } from './components/EventCard';
import { DonationSection } from './components/DonationSection';
import { Footer } from './components/Footer';
import { sampleEvents, categories } from './data/sampleEvents';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');

  // Filter events based on search term, category, and date
  const filteredEvents = useMemo(() => {
    return sampleEvents.filter(event => {
      const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           event.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           event.location.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === 'All' || event.category === selectedCategory;
      
      // Simple date filtering (in a real app, this would be more sophisticated)
      let matchesDate = true;
      if (selectedDate) {
        const eventDate = new Date(event.date);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        switch (selectedDate) {
          case 'today':
            matchesDate = eventDate.toDateString() === today.toDateString();
            break;
          case 'tomorrow':
            matchesDate = eventDate.toDateString() === tomorrow.toDateString();
            break;
          case 'this-week':
            const weekFromNow = new Date(today);
            weekFromNow.setDate(weekFromNow.getDate() + 7);
            matchesDate = eventDate >= today && eventDate <= weekFromNow;
            break;
          case 'this-weekend':
            const saturday = new Date(today);
            const sunday = new Date(today);
            saturday.setDate(saturday.getDate() + (6 - saturday.getDay()));
            sunday.setDate(sunday.getDate() + (7 - sunday.getDay()));
            matchesDate = eventDate >= saturday && eventDate <= sunday;
            break;
          default:
            matchesDate = true;
        }
      }
      
      return matchesSearch && matchesCategory && matchesDate;
    });
  }, [searchTerm, selectedCategory, selectedDate]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Filter Bar */}
        <div className="mb-8">
          <FilterBar
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            categories={categories}
            selectedDate={selectedDate}
            setSelectedDate={setSelectedDate}
          />
        </div>

        {/* Results Summary */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {filteredEvents.length} {filteredEvents.length === 1 ? 'Event' : 'Events'} Found
          </h2>
          <p className="text-muted-foreground">
            Discover amazing free and low-cost activities in Amsterdam
          </p>
        </div>

        {/* Events Grid */}
        {filteredEvents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {filteredEvents.map(event => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search criteria or check back later for new events.
            </p>
          </div>
        )}

        {/* Donation Section */}
        <div id="donation" className="mb-8">
          <DonationSection />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
