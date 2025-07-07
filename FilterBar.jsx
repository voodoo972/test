import { Search, Filter, Calendar } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function FilterBar({ 
  searchTerm, 
  setSearchTerm, 
  selectedCategory, 
  setSelectedCategory, 
  categories,
  selectedDate,
  setSelectedDate 
}) {
  const clearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('All');
    setSelectedDate('');
  };

  const hasActiveFilters = searchTerm || selectedCategory !== 'All' || selectedDate;

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search events..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Category Filter */}
        <div className="w-full lg:w-48">
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Date Filter */}
        <div className="w-full lg:w-48">
          <select 
            value={selectedDate} 
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All dates</option>
            <option value="today">Today</option>
            <option value="tomorrow">Tomorrow</option>
            <option value="this-week">This week</option>
            <option value="this-weekend">This weekend</option>
          </select>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <Button variant="outline" onClick={clearFilters} className="lg:w-auto">
            <Filter className="h-4 w-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t">
          {searchTerm && (
            <Badge variant="secondary">
              Search: "{searchTerm}"
            </Badge>
          )}
          {selectedCategory !== 'All' && (
            <Badge variant="secondary">
              Category: {selectedCategory}
            </Badge>
          )}
          {selectedDate && (
            <Badge variant="secondary">
              Date: {selectedDate.replace('-', ' ')}
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}

