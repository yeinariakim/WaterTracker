import os, json
import firebase_admin
from firebase_admin import credentials, firestore, messaging

cred_json = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
cred = credentials.Certificate(cred_json)
firebase_admin.initialize_app(cred)
db = firestore.client()

# cron-job.org가 workflow_dispatch로 넘겨주는 알림 칸 이름이에요.
slot = os.environ.get('SLOT', '').strip()
messages_map = {
    'w1': '💧',          # 평일 10:00
    'w2': '💧💧',        # 평일 11:30
    'w3': '💧💧💧',      # 평일 14:00
    'w4': '💧💧💧💧',    # 평일 16:00
    'w5': '💧💧💧💧💧',  # 평일 18:00
    'e1': '💧',          # 주말 11:00
    'e2': '💧',          # 주말 14:00
    'e3': '💧',          # 주말 17:00
}
body = messages_map.get(slot, '물 마실 시간이에요 (테스트)')
print(f'slot={slot!r} -> {body}')

tokens = []
for doc in db.collection('users').stream():
    d = doc.to_dict() or {}
    toks = d.get('fcmTokens') or []
    tokens.extend(toks)
tokens = list(set(tokens))
print(f'sending to {len(tokens)} token(s)')

for t in tokens:
    try:
        msg = messaging.Message(
            notification=messaging.Notification(title=body),
            # 기기가 꺼져 있다가 30분 넘게 지나서 켜지면 이 알림은 버려요
            webpush=messaging.WebpushConfig(headers={'TTL': '1800', 'Urgency': 'high'}),
            token=t,
        )
        messaging.send(msg)
        print('sent OK to', t[:12] + '...')
    except Exception as e:
        print('failed for token', t[:12] + '...', '-', e)
