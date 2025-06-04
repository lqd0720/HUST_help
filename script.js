let data = [];

fetch('courses.json')
  .then(res => res.json())
  .then(json => {
    data = json;
    displayCourses(data);
  });

document.getElementById('searchInput').addEventListener('input', (e) => {
  const keyword = e.target.value.toLowerCase();
  const filtered = data.filter(course =>
    course["Mã học phần"].toLowerCase().includes(keyword) ||
    course["Tên học phần"].toLowerCase().includes(keyword)
  );
  displayCourses(filtered);
});

function displayCourses(courses) {
  const container = document.getElementById('results');
  container.innerHTML = '';

  if (courses.length === 0) {
    container.innerHTML = '<p>Không tìm thấy học phần nào.</p>';
    return;
  }

  courses.forEach(course => {
    const div = document.createElement('div');
    div.className = 'course';
    div.innerHTML = `
      <div class="course-title">${course["Mã học phần"]}: ${course["Tên học phần"]}</div>
      <div>Thời lượng: ${course["Thời lượng"]}</div>
      <div>Tín chỉ: ${course["Tín chỉ"]}</div>
      <div>Trọng số: ${course["Trọng số"]}</div>
    `;
    container.appendChild(div);
  });
}
