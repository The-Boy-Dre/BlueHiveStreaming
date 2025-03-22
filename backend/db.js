// backend/db.js
const { MongoClient } = require('mongodb');

const MONGO_URI = 'mongodb://127.0.0.1:27017';
const DB_NAME = 'streamingapp';

async function connectDB() {
  try {
    const client = new MongoClient(MONGO_URI);
    await client.connect();
    console.log('Connected to MongoDB');
    const db = client.db(DB_NAME);
    // You can store this db instance in a global or pass it around as needed
    return db;
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
  }
}

module.exports = { connectDB };
