console.log("TimeTable App Loaded");
// ✅ 1. 時間帯をクリックで選択・解除
document.querySelectorAll('.time-slot').forEach(slot => {
  slot.addEventListener('click', () => {
    slot.classList.toggle('selected');
  });
});

// ✅ 2. 選択した時間帯をサーバーに送信
document.getElementById('submit-timetable').addEventListener('click', () => {
  const selectedTimes = Array.from(document.querySelectorAll('.selected'))
    .map(el => el.dataset.time); // 例: data-time="09:00"

  fetch('/submit-timetable', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ times: selectedTimes })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message || '保存しました');
  });
});

// ✅ 3. 初期表示で保存済みの時間帯を読み込む
window.addEventListener('DOMContentLoaded', () => {
  fetch('/get-timetable')
    .then(res => res.json())
    .then(data => {
      data.times.forEach(time => {
        const slot = document.querySelector(`[data-time="${time}"]`);
        if (slot) slot.classList.add('selected');
      });
    });
});
