// lib/redis.js
import Redis from 'ioredis';

const redis = new Redis({
  host: 'localhost', // Or your Redis server IP / Docker hostname
  port: 6379,
  db: 0,
});

export default redis;
