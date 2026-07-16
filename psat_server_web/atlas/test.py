from atlasapiclient.client import RequestCustomListsTable

OBJECTGROUPID = 73  # TODO Ken: replace with your real list id
DEC_GTE = 10

payload = {'objectgroupid': OBJECTGROUPID, 'dec_gte': DEC_GTE}

client = RequestCustomListsTable(payload=payload, get_response=True)
rows = client.response_data

group_ids = sorted(set(row['object_group_id'] for row in rows))
print("requested objectgroupid:", OBJECTGROUPID)
print("distinct object_group_id in response:", group_ids)
print("total rows:", len(rows))
