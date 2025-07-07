import { Heart, Coffee, Gift } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export function DonationSection() {
  const donationAmounts = [
    { amount: 3, icon: Coffee, label: "Buy us a coffee" },
    { amount: 10, icon: Heart, label: "Show some love" },
    { amount: 25, icon: Gift, label: "Be generous" }
  ];

  const handleDonation = (amount) => {
    // In a real implementation, this would integrate with a payment processor
    alert(`Thank you for your ${amount}€ donation! This would redirect to a payment processor.`);
  };

  return (
    <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center gap-2 text-xl">
          <Heart className="h-6 w-6 text-red-500" />
          Support Amsterdam Events
        </CardTitle>
        <p className="text-muted-foreground">
          Help us keep this service free and discover more amazing events in Amsterdam
        </p>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {donationAmounts.map(({ amount, icon: Icon, label }) => (
            <Button
              key={amount}
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-blue-100 hover:border-blue-300 transition-colors"
              onClick={() => handleDonation(amount)}
            >
              <Icon className="h-6 w-6 text-blue-600" />
              <div className="text-center">
                <div className="font-semibold">€{amount}</div>
                <div className="text-xs text-muted-foreground">{label}</div>
              </div>
            </Button>
          ))}
        </div>
        
        <div className="mt-4 text-center">
          <Button 
            variant="link" 
            className="text-sm text-muted-foreground"
            onClick={() => handleDonation('custom')}
          >
            Or choose a custom amount
          </Button>
        </div>
        
        <div className="mt-4 text-xs text-center text-muted-foreground">
          <p>
            Your donations help us maintain the website, discover new events, and keep everything free for the community.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

