CREATE KEYSPACE Asset WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };

CREATE TABLE asset.asset_by_user_id (
   user_id TEXT,
   asset_name TEXT,
   time timestamp,

   PRIMARY KEY (user_id, time)
) WITH CLUSTERING ORDER BY (time DESC);

CREATE TABLE asset.asset_by_asset_name(
   asset_name TEXT,
   user_id TEXT,
   time timestamp,

   PRIMARY KEY (asset_name, time)
) WITH CLUSTERING ORDER BY (time DESC);
