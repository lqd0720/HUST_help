import { useState, useEffect } from 'react';

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`);
      const data = await res.json();
      setCourses(data);
    };

    // Debounce: wait 300ms after typing
    const timeout = setTimeout(fetchData, 300);
    return () => clearTimeout(timeout);
  }, [searchTerm]);

  return (
    <main style={{ padding: 20, maxWidth: 800, margin: 'auto' }}>
      <h1>Course Catalog</h1>
      <input
        type="search"
        placeholder="Search by code or name..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        style={{ width: '100%', padding: 12, marginBottom: 20, fontSize: '1rem' }}
        autoFocus
      />
      <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
        {courses.length === 0 ? (
          <li>No matching courses.</li>
        ) : (
          courses.map(course => (
            <li key={course['Mã học phần']} style={{ padding: 10, borderBottom: '1px solid #eee' }}>
              <strong>{course['Mã học phần']}</strong> - {course['Tên học phần']}
            </li>
          ))
        )}
      </ul>
    </main>
  );
}
