db = db.getSiblingDB('map_db');

db.createUser({
  user: "mongo_user",
  pwd: "mongo_pass",
  roles: [{ role: "readWrite", db: "map_db" }]
});

db = db.getSiblingDB('station_db'); 

db.createUser({
  user: "mongo_user",
  pwd: "mongo_pass",
  roles: [{ role: "readWrite", db: "station_db" }]
});

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
