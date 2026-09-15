import os, json
import firebase_admin
from firebase_admin import credentials, firestore, messaging

cred_json = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
cred = credentials.Certificate(cred_json)
firebase_admin.initialize_app(cred)
db = firestore.client()

schedule = os.environ.get('SCHEDULE', '')
messages_map = {
    '0 1 * * 1-5':  '오전 1잔 마실 시간이에요 (10:00)',
    '30 2 * * 1-5': '오전 2잔 마실 시간이에요 (11:30)',
    '0 5 * * 1-5':  '오후 1잔 마실 시간이에요 (14:00)',
    '30 7 * * 1-5': '오후 2잔 마실 시간이에요 (16:30)',
    '0 9 * * 1-5':  '오후 3잔 마실 시간이에요 (18:00)',
}
body = messages_map.get(schedule, '물 마실 시간이에요 (테스트)')

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
            notification=messaging.Notification(title='💧 물마시기 알림', body=body),
            token=t,
        )
        messaging.send(msg)
        print('sent OK to', t[:12] + '...')
    except Exception as e:
        print('failed for token', t[:12] + '...', '-', e)
