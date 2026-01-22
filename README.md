import { useState } from 'react';
import { Header } from './components/Header';
import { HomePage } from './components/HomePage';
import { CitizenDetail } from './components/CitizenDetail';
import { ResearcherDetail } from './components/ResearcherDetail';
import { CommunityDetail } from './components/CommunityDetail';
import { BottomNav } from './components/BottomNav';
import { Chatbot } from './components/Chatbot';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [activeScreen, setActiveScreen] = useState<string | null>(null);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  const handleBack = () => {
    setActiveScreen(null);
  };

  const handleNavigate = (screen: string) => {
    setActiveScreen(screen);
  };

  const renderContent = () => {
    // If there's an active screen from navigation, show it
    if (activeScreen === 'citizen') {
      return <CitizenDetail onBack={handleBack} />;
    }
    if (activeScreen === 'researcher') {
      return <ResearcherDetail onBack={handleBack} />;
    }

    // Otherwise show content based on active tab
    switch (activeTab) {
      case 'home':
        return (
          <>
            <Header />
            <HomePage onNavigate={handleNavigate} />
          </>
        );
      case 'community':
        return <CommunityDetail onBack={() => setActiveTab('home')} />;
      default:
        return (
          <>
            <Header />
            <HomePage onNavigate={handleNavigate} />
          </>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e27] text-white">
      <div className="max-w-md mx-auto min-h-screen bg-[#0a0e27] relative pb-20">
        {renderContent()}
        <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
        <Chatbot isOpen={isChatbotOpen} onToggle={() => setIsChatbotOpen(!isChatbotOpen)} />
      </div>
    </div>
  );
}
