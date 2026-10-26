# Kamailio SBC — Debian 12 Docker lab

Production-oriented development lab เท่านั้น: ไม่ใช่ production SBC พร้อม deploy
ไฟล์จาก Cloud Task เดิมหายไปใน Workspace นี้ โครงการนี้สร้างใหม่ ไม่ใช่กู้คืน
ไม่มี commit/push/deploy หรือแก้ directory อื่นใน repository

## เริ่มต้น

ต้องมี Docker Engine, Compose v2, host Python 3 และ OpenSSL
จาก directory `kamailio/`:

```sh
docker compose config --quiet
docker compose build
# ถ้า Buildx state directory อ่านอย่างเดียว ให้ใช้ fallback ที่ทดสอบจริง:
DOCKER_BUILDKIT=0 docker build -t kamailio-sbc-lab:dev .
chmod 755 config
chmod 644 config/*.cfg
docker compose up -d --no-build
docker compose exec -T sip-tester python3 /opt/lab/tests/signaling.py
```

TLS/WSS ใช้ CA เฉพาะ Lab อายุสองวัน ไม่ใช่ production certificate:

```sh
sh scripts/test-cert.sh
docker compose -f compose.yaml -f compose.tls.yaml config --quiet
docker compose -f compose.yaml -f compose.tls.yaml up -d --no-build
docker compose -f compose.yaml -f compose.tls.yaml exec -T sip-tester \
  python3 /opt/lab/tests/signaling.py --tls
```

ทดสอบอาจต้องรอ startup; ตรวจ logs/health ก่อน retry และห้ามวนซ้ำโดยไม่วินิจฉัย
private key อยู่ ignored .runtime/ ไม่ควรนำขึ้น Git; script ไม่ overwrite keys เดิม
หลังแก้ mounted config ให้ restart SBC เพื่อ render ค่าและโหลด config ใหม่

```sh
docker compose -f compose.yaml -f compose.tls.yaml logs kamailio
docker compose exec -T kamailio kamailio -c -f /tmp/kamailio.cfg
docker compose -f compose.yaml -f compose.tls.yaml down
```

`down` ใช้เฉพาะ disposable project นี้ ไม่ใช้ -v และไม่ prune image/volume
ไม่มี Docker volumes สำหรับ persistent database เพราะยังไม่เปิด database

## ขอบเขต

- external/internal Docker networks แยกกัน, internal SIP ไม่ publish
- SIP UDP/TCP, optional TLS/WSS, host ports bind เฉพาะ 127.0.0.1
- Source + destination allowlists, sanity, Max-Forwards, transactions,
  dispatcher ไป single mock backend; REGISTER ถูกปิด
- mock-freeswitch เป็น Python SIP stub ไม่ใช่ FreeSWITCH จริง
- Reverse dialogs ถูกปิดจนกว่าจะมี contact/flow ownership ที่ทดสอบแล้ว
- RTPengine แยก image/service, userspace เท่านั้น; ไม่ต่อเข้ากับ SDP routing
- ไม่มี database, SIP trunk จริง, AWS credentials, public port หรือ deployment

## เอกสารและหลักฐาน

- [Architecture / protocols / gaps](docs/architecture.md)
- [Official sources and versions](docs/sources.md)
- [Actual module inventory](docs/module-evidence.txt)
- [Test report](docs/test-report.md), [raw command evidence](docs/test-results.json)
- [Operations / storage / rollback / security](docs/operations.md)
- [Database decision](database/README.md)
- [RTPengine scope](rtpengine/README.md)
- [CI / Draft PR plan](docs/ci-plan.md)

`compose.prod.yaml` เป็น standalone design scaffold มี required variables,
ไม่ใช่ override ที่รวม development mock/tester เข้า production และยัง deploy ไม่ได้
จนกว่าจะมี reviewed production config, actual interfaces/certs/ACL และ acceptance
ทุกคำกล่าวอ้างผลทดสอบต้องอ้าง docs/test-results.json ไม่ใช่เพียงมีไฟล์ configuration

ตรวจ TLS negative policy และ network exposure (จาก `kamailio/`):

```sh
docker compose -f compose.yaml -f compose.tls.yaml exec -T sip-tester \
  python3 - < tests/security.py
python3 tests/exposure.py
```

คำสั่ง exposure ต้องใช้ host Docker CLI; เป็นการตรวจ metadata แบบอ่านอย่างเดียว
