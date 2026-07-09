# Task Kyle

**Ver Show1**

Task Kyleは, テキストベースで簡単に予定登録ができるアプリになっております.
現在は, Google Calendarと連携し, 登録・変更・削除を行えるように開発を進めています.
また, Discordと連携し, 予定の登録・変更・削除そして通知を行えるようにしています.

[Owner site](https://jeshika0815.github.io/tom2005_webs/)

### 開発ユーザ
- Jeshika0815
- ZAKKTH
- ryoubaiwarabe-creator

---
## インストール方法
1. 自身の環境でDockerがインストールされているかを確認ください. Dockerは[こちら](https://www.docker.com/get-started)よりインストールしてください.
2. 以下のスクリプトを用いてインストールを行なってください.

Linux/MacOS
```sh
curl -sSL https://jeshika0815.github.io/tom2005_webs/app_install/task_kyle_app/nsetup.sh | bash
```

Windows
```bat
curl -sSL https://jeshika0815.github.io/tom2005_webs/app_install/task_kyle_app/setup.bat | cmd
```

3. インストールが完了したら, 起動したいアプリ`task_kyle_app`あるいは`task_kyle_app/frontend`にて`docker-compose up -d`を実行して起動してください.
