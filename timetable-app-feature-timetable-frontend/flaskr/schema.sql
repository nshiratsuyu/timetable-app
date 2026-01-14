DROP TABLE IF EXISTS blogs;

CREATE TABLE blogs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    user_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

INSERT INTO blogs (id,title, body, user_name)
VALUES (1,'ごはん日記', 'お昼はカルボナーラ', 'yuki'),
(2,'好きな曲リスト', 'インフェルノ/ Mrs.Gただ君に晴れ/ヨルシカ', 'mai'),
(3, '気になる本', 'ファッション・パーツ図鑑', 'yuki');
