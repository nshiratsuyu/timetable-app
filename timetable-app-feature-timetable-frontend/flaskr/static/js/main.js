console.log("JS 読み込まれたよ！時間割保存版");

// 保存ボタン（💾）を押した時の動作
const saveBtn = document.getElementById("save-button");
if (saveBtn) {
    saveBtn.addEventListener("click", function() {
        alert("保存ボタンが押されました！バックエンドにデータを送る準備をします。");
        
        // ここにデータを保存する処理を書けます
        fetch('/api/lessons', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            console.log("現在の授業データ:", data);
            alert("サーバーからデータを取得しました！コンソールを見てください。");
        });
    });
}