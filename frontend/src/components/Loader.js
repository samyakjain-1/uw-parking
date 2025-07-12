import React from 'react';
import './Loader.css';

const Loader = () => {
  return (
    <div className="loader-container">
      <div className="terminal-loader">
        <div className="terminal-header">
          <div className="terminal-title">Status</div>
          <div className="terminal-controls">
            <div className="control close"></div>
            <div className="control minimize"></div>
            <div className="control maximize"></div>
          </div>
        </div>
        <div className="text">This app is asleep, waking it up... (this might take a moment)</div>
      </div>
    </div>
  );
};

export default Loader;
