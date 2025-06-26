import React from 'react';
import './GarageList.css';

const GarageList = ({ garages, onGarageSelect, onClose }) => {
  if (!garages || garages.length === 0) {
    return null;
  }

  return (
    <div className="garage-list-container">
      <button onClick={onClose} className="close-button">&times;</button>
      <h2>Available Garages (Nearest First)</h2>
      <ul className="garage-list">
        {garages.map((garage) => (
          <li key={garage.id} onClick={() => onGarageSelect(garage)}>
            <div className="garage-info">
              <strong>{garage.name}</strong>
              <span>{garage.distance.toFixed(2)} miles away</span>
            </div>
            <div className="garage-availability">
              <span>{garage.vacant_stalls}</span>
              <small>spaces</small>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GarageList;
