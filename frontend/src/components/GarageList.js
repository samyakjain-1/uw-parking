import React from 'react';
import './GarageList.css';

// Helper to normalize rate strings to a per-hour format
const normalizeRate = (rateString) => {
  if (!rateString || typeof rateString !== 'string') return "N/A";
  if (rateString.toLowerCase() === 'free') return "Free";
  
  const per30MinMatch = rateString.match(/\$(\d+(\.\d+)?)\/30min/);
  if (per30MinMatch) {
    const price = parseFloat(per30MinMatch[1]) * 2;
    return `$${price.toFixed(2)}/hr`;
  }

  const perHourMatch = rateString.match(/\$(\d+(\.\d+)?)\/hr/);
  if (perHourMatch) {
    const price = parseFloat(perHourMatch[1]);
    return `$${price.toFixed(2)}/hr`;
  }
  
  return rateString.split(' ')[0]; // Fallback to the first part of the string
};

// Helper to determine the current rate based on time
const getCurrentRate = (garage) => {
  const now = new Date();
  const day = now.getDay(); 
  const hour = now.getHours();

  const isWeekday = day >= 1 && day <= 5;
  const isDaytime = hour >= 7 && hour < 16.5;
  const isEvening = hour >= 16.5 && hour < 24;

  let rate;
  if (garage.notes.includes("Enforced at all times")) {
    rate = hour >= 7 ? garage.daytime_rate : garage.evening_rate;
  } else if (garage.notes.includes("all day Sat/Sun")) {
    if (!isWeekday) rate = "Free";
    else if (isDaytime) rate = garage.daytime_rate;
    else if (isEvening) rate = garage.evening_rate;
    else rate = "Free";
  } else if (garage.notes.includes("all day Sun")) {
    if (day === 0) rate = "Free";
    else if (isDaytime) rate = garage.daytime_rate;
    else if (isEvening) rate = garage.evening_rate;
    else rate = "Free";
  } else if (garage.notes.includes("daily")) {
    if (isDaytime) rate = garage.daytime_rate;
    else if (isEvening) rate = garage.evening_rate;
    else rate = "Free";
  } else {
    rate = "N/A";
  }
  
  return normalizeRate(rate);
};


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
            <div className="garage-details">
              <div className="garage-availability">
                <span>{garage.vacant_stalls}</span>
                <small>spaces</small>
              </div>
              <div className="garage-rate">
                <span>{getCurrentRate(garage)}</span>
                <small>current rate</small>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GarageList;
