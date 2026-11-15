import { useState } from 'react';
import Team from './components/Team';
import Absences from './components/Absences';
import Backlog from './components/Backlog';
import Planning from './components/Planning';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('planning');

  return (
    <div className="app">
      <header className="header">
        <h1 className="header__title">Sprint Planner</h1>
        <nav className="nav">
          <button 
            className={`nav__button ${activeTab === 'team' ? 'nav__button--active' : ''}`}
            onClick={() => setActiveTab('team')}
          >
            Команда
          </button>
          <button 
            className={`nav__button ${activeTab === 'absences' ? 'nav__button--active' : ''}`}
            onClick={() => setActiveTab('absences')}
          >
            Отпуска
          </button>
          <button 
            className={`nav__button ${activeTab === 'backlog' ? 'nav__button--active' : ''}`}
            onClick={() => setActiveTab('backlog')}
          >
            Бэклог
          </button>
          <button 
            className={`nav__button ${activeTab === 'planning' ? 'nav__button--active' : ''}`}
            onClick={() => setActiveTab('planning')}
          >
            Планирование
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'team' && <Team />}
        {activeTab === 'absences' && <Absences />}
        {activeTab === 'backlog' && <Backlog />}
        {activeTab === 'planning' && <Planning />}
      </main>
    </div>
  );
}

export default App;