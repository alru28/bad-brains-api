db = db.getSiblingDB('map_db');

db.createUser({
  user: "mongo_user",
  pwd: "mongo_pass",
  roles: [{ role: "readWrite", db: "map_db" }]
});

// Insert locations
db.locations.insertMany([
  {
    location_id: "location_1",
    address: "Av. Lehendakari Aguirre 11, Bilbao",
    information: "Non-profit organization for deaf people",
    type: "LOCATION",
    lat: 43.271586,
    long: -2.944325,
    comments: [
      { username: "user1", text: "Great location if you are looking for assistance or information regarding deaf accessibility." },
      { username: "user2", text: "Quite a deaf-friendly place!" }
    ]
  },
  {
    location_id: "station_1",
    address: "123 Main St, Cityville",
    information: "Station with multiple charging safes available.",
    type: "STATION",
    lat: 40.712776,
    long: -74.005974,
    comments: [
      { username: "user1", text: "Convenient station!" },
      { username: "user3", text: "Pretty convenient when you need to stock quickly on disposable batteries." }
    ]
  },
  {
    location_id: "station_2",
    address: "456 Side St, Townsville",
    information: "Station with charging options for hearing aids.",
    type: "STATION",
    lat: 34.052235,
    long: -118.243683,
    comments: [
      { username: "user2", text: "Good station, but needs more slots." }
    ]
  }
]);

// Insert stations
db.stations.insertMany([
  {
    station_id: "station_1",
    address: "123 Main St, Cityville",
    safes: [
      { safe_id: 1, reserved_until: null, pin: null },
      { safe_id: 2, reserved_until: null, pin: null },
      { safe_id: 3, reserved_until: null, pin: null }
    ]
  },
  {
    station_id: "station_2",
    address: "456 Side St, Townsville",
    safes: [
      { safe_id: 1, reserved_until: null, pin: null },
      { safe_id: 2, reserved_until: null, pin: null }
    ]
  }
]);
