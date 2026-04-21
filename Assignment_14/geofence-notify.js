// Geofence Notification System
// This utility handles geofence checking and notification logic

class GeofenceNotifier {
    constructor(centerLat, centerLon, radiusKm) {
        this.centerLat = centerLat;
        this.centerLon = centerLon;
        this.radiusKm = radiusKm;
        this.previouslyInside = false;
    }

    /**
     * Calculate distance between two coordinates using Haversine formula
     * @param {number} lat1 - Latitude of point 1
     * @param {number} lon1 - Longitude of point 1
     * @param {number} lat2 - Latitude of point 2
     * @param {number} lon2 - Longitude of point 2
     * @returns {number} Distance in kilometers
     */
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = 
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    /**
     * Check if coordinates are inside geofence
     * @param {number} lat - Current latitude
     * @param {number} lon - Current longitude
     * @returns {boolean} True if inside geofence
     */
    isInsideGeofence(lat, lon) {
        const distance = this.calculateDistance(this.centerLat, this.centerLon, lat, lon);
        return distance <= this.radiusKm;
    }

    /**
     * Check for geofence boundary crossing
     * @param {number} lat - Current latitude
     * @param {number} lon - Current longitude
     * @returns {object} Event details { entered: boolean, exited: boolean, distance: number }
     */
    checkBoundaryCross(lat, lon) {
        const isInside = this.isInsideGeofence(lat, lon);
        const distance = this.calculateDistance(this.centerLat, this.centerLon, lat, lon);
        
        const event = {
            isInside: isInside,
            distance: distance.toFixed(2),
            entered: false,
            exited: false
        };

        // Detect boundary crossing
        if (isInside && !this.previouslyInside) {
            event.entered = true; // Just entered
        } else if (!isInside && this.previouslyInside) {
            event.exited = true; // Just exited
        }

        this.previouslyInside = isInside;
        return event;
    }
}

// Usage example:
// const notifier = new GeofenceNotifier(40.7128, -74.0060, 5); // NYC, 5km radius
// const gpsData = { latitude: 40.7580, longitude: -73.9855 }; // Times Square
// const event = notifier.checkBoundaryCross(gpsData.latitude, gpsData.longitude);
// if (event.entered) { sendNotification("You entered the geofence"); }
// if (event.exited) { sendNotification("You exited the geofence"); }
