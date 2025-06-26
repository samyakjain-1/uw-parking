import React, { useState, useEffect, useMemo } from 'react';
import { APIProvider, Map, AdvancedMarker, Pin, InfoWindow, useApiIsLoaded } from '@vis.gl/react-google-maps';
import PlacesAutocomplete from './components/PlacesAutocomplete';
import GarageList from './components/GarageList';
import MapController from './components/MapController';
import './App.css';

// Haversine formula to calculate distance between two lat/lng points
const haversineDistance = (coords1, coords2) => {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 3959; // Earth radius in miles

  const dLat = toRad(coords2.lat - coords1.lat);
  const dLon = toRad(coords2.lng - coords1.lng);
  const lat1 = toRad(coords1.lat);
  const lat2 = toRad(coords2.lat);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c; // Distance in miles
};

const MapContainer = () => {
  const [allGarages, setAllGarages] = useState([]);
  const [selectedGarage, setSelectedGarage] = useState(null);
  const [destination, setDestination] = useState(null);
  const [showGarageList, setShowGarageList] = useState(false);
  const [mapCenter, setMapCenter] = useState({ lat: 43.07659, lng: -89.41248 });
  const [mapZoom, setMapZoom] = useState(14);
  const apiIsLoaded = useApiIsLoaded();

  useEffect(() => {
    const fetchGarages = async () => {
      try {
        const response = await fetch('/api/garages');
        const data = await response.json();
        const validGarages = data.filter(g => g.latitude && g.longitude);
        setAllGarages(validGarages);
      } catch (error) {
        console.error("Error fetching garage data:", error);
      }
    };
    fetchGarages();
    const intervalId = setInterval(fetchGarages, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const handleDestinationSelect = (dest) => {
    setDestination(dest);
    setShowGarageList(true);
    setMapCenter(dest);
    setMapZoom(15);
  };

  const handleGarageSelect = (garage) => {
    setSelectedGarage(garage);
    setShowGarageList(false); // Hide list when a garage is selected from it
    setMapCenter({ lat: garage.latitude, lng: garage.longitude });
    setMapZoom(17);
  };

  const handleCloseList = () => {
    setDestination(null);
    setShowGarageList(false);
    setMapCenter({ lat: 43.07659, lng: -89.41248 }); // Reset map center
    setMapZoom(14); // Reset map zoom
  };

  const availableGarages = useMemo(() => {
    if (!destination) {
      return allGarages.map(g => ({ ...g, distance: null }));
    }
    return allGarages
      .filter(g => g.vacant_stalls !== 'FULL' && !isNaN(parseInt(g.vacant_stalls, 10)))
      .map(g => ({
        ...g,
        distance: haversineDistance(
          { lat: destination.lat, lng: destination.lng },
          { lat: g.latitude, lng: g.longitude }
        ),
      }))
      .sort((a, b) => a.distance - b.distance);
  }, [allGarages, destination]);

  const getPinProps = (availability) => {
    const vacantStalls = parseInt(availability, 10);
    if (availability === 'FULL') return { background: '#d9534f', borderColor: '#d43f3a', glyphColor: '#ffffff' };
    if (!isNaN(vacantStalls)) {
      if (vacantStalls < 5) return { background: '#f0ad4e', borderColor: '#eea236', glyphColor: '#ffffff' };
      return { background: '#5cb85c', borderColor: '#4cae4c', glyphColor: '#ffffff' };
    }
    return { background: '#777777', borderColor: '#666666', glyphColor: '#ffffff' };
  };

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      {apiIsLoaded && <PlacesAutocomplete onSelect={handleDestinationSelect} />}
      {showGarageList && (
        <GarageList 
          garages={availableGarages} 
          onGarageSelect={handleGarageSelect} 
          onClose={handleCloseList} 
        />
      )}
      
      <Map defaultCenter={mapCenter} defaultZoom={mapZoom} mapId="uw-madison-map" gestureHandling={'greedy'}>
        <MapController center={mapCenter} zoom={mapZoom} />
        {availableGarages.map((garage) => {
          const pinProps = getPinProps(garage.vacant_stalls);
          return (
            <AdvancedMarker
              key={garage.id}
              position={{ lat: garage.latitude, lng: garage.longitude }}
              onClick={() => handleGarageSelect(garage)}
            >
              <Pin {...pinProps} />
            </AdvancedMarker>
          );
        })}

        {destination && (
          <AdvancedMarker position={destination} title="Your Destination">
            <Pin background={'#6329a8'} borderColor={'#4a1e7d'} glyphColor={'#ffffff'} />
          </AdvancedMarker>
        )}

        {selectedGarage && (
          <InfoWindow
            position={{ lat: selectedGarage.latitude, lng: selectedGarage.longitude }}
            onCloseClick={() => setSelectedGarage(null)}
          >
            <div>
              <h3>{selectedGarage.name}</h3>
              <p><strong>Availability:</strong> {selectedGarage.vacant_stalls || 'N/A'}</p>
              {selectedGarage.distance !== null && (
                <p><strong>Distance:</strong> {selectedGarage.distance.toFixed(2)} miles</p>
              )}
              <p><strong>Address:</strong> {selectedGarage.address}</p>
              <p><small>Last updated: {new Date(selectedGarage.timestamp).toLocaleString()}</small></p>
            </div>
          </InfoWindow>
        )}
      </Map>
    </div>
  );
}

const App = () => {
  const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || "YOUR_GOOGLE_MAPS_API_KEY";

  if (apiKey === "YOUR_GOOGLE_MAPS_API_KEY") {
    return <div className="App"><h1>Google Maps API Key Needed</h1>...</div>;
  }

  return (
    <APIProvider apiKey={apiKey} libraries={['places']}>
      <MapContainer />
    </APIProvider>
  );
};

export default App;
