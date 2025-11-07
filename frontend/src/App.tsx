import React from 'react';
import logo from './logo.svg';
import './App.css';
import MainScreen from './pages/mainScreen';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <MainScreen/>
      </header>
    </div>
  );
}

export default App;
