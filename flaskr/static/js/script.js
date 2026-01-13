console.log("JS 読み込まれたよ！");

const picker = document.querySelector('#picker');

const setBgColor = () => {
  document.body.style.backgroundColor = picker.value;
}

picker.addEventListener('input', setBgColor);

document.getElementById("ai-comment-btn").addEventListener("click", function() {
    const blogId = this.dataset.blogId;

    fetch(`/blogs/${blogId}/ai-comment`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const li = document.createElement("li");
            li.innerHTML = `<strong>${data.user_name}:</strong> ${data.body}`;
            document.getElementById("comment-list").appendChild(li);
        } else {
            alert("コメント追加に失敗しました");
        }
    });
});
