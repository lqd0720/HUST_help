// pages/api/search.js
import redis from '@/lib/redis';

export default async function handler(req, res) {
  const query = (req.query.q || '').toLowerCase();

  // Get all course keys
  const keys = await redis.keys('course:*');

  const results = [];
  for (const key of keys) {
    const course = await redis.hgetall(key);

    // Filter by course name or code
    if (
      course['Mã học phần']?.toLowerCase().includes(query) ||
      course['Tên học phần']?.toLowerCase().includes(query)
    ) {
      results.push(course);
    }
  }

  res.status(200).json(results);
}
