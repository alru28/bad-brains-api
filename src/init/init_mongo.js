db = db.getSiblingDB('map_db');  // Switch to the target database

db.createUser({
  user: "mongo_user",
  pwd: "mongo_pass",
  roles: [{ role: "readWrite", db: "map_db" }]
});