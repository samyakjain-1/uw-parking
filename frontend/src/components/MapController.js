import { useEffect } from 'react';
import { useMap } from '@vis.gl/react-google-maps';

const MapController = ({ center, zoom }) => {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    // Use the map's imperative methods for smooth transitions
    map.panTo(center);
    map.setZoom(zoom);
  }, [map, center, zoom]);

  // This component does not render anything itself
  return null;
};

export default MapController;
